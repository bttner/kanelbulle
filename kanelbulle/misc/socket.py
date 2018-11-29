"""Utilities related to socket communication."""

import json
import socket
import time
from PyQt5.QtCore import QThread, pyqtSignal
from kanelbulle.config import config
from kanelbulle.gui.socketinterface import SocketInterface


class SocketServer:

    """A socket server with the capability to send/receive strings and
    JSON files.

    Attributes:
        logger: The used logger.
        socket: The socket interface.
        client_conn: Socket object usable to send and receive data on the
        connection.
        client_addr: Address bound to the socket on the other end of the
        connection.
    """

    backlog = 1

    def __init__(self, logger):
        self.logger = logger
        self.socket = None
        self.client_conn = None
        self.client_addr = None

    def create(self, host, port):
        """Creates a server.

        Args:
            host: Represents either a hostname or an IPv4 address.
            port: The port.

        Return:
            - True, if the server could be started.
            - False, if not.
        """
        if isinstance(host, str) and isinstance(port, int):
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.socket.bind((host, port))
                self.socket.listen(self.backlog)
            except socket.error as e:
                self.logger.error('SERVER | Error, the server could not be '
                                  'started. Reason: {}'.format(e))
                return False
        else:
            self.logger.error('SERVER | Error, the server could not be '
                              'started. Reason: Data type violation. The host '
                              'number has to be provided as a string and the '
                              'port number as an integer.')
            return False

        self.logger.info('SERVER | Created server at (host, port) = ({}, '
                         '{}).'.format(host, port))
        self.logger.info("SERVER | Listening for connections.")
        return True

    def accept(self):
        """Accepts a connection."""
        try:
            self.client_conn, self.client_addr = self.socket.accept()
        except socket.timeout:
            return False

        self.logger.info("SERVER | Connection to client accepted. The "
                         "client IP is: {}.".format(self.client_addr))
        return True

    def send(self, data, path=False):
        """Sends data to the socket in two steps.
            1. step: Sends the length of the message.
            2. step: Sends the original message.

        Args:
            data: The data to send.
            path: If the data to send is within a file, path equals True.
            Otherwise path is False.

        Return:
            - [#1, #2]
                #1: True if a client is connected, False if not.
                #2: True if the data to be send is as expected, False if not.
        """
        if not self.client_conn:
            self.logger.error('SERVER | Error, can not send message. Reason: '
                              'No client is connected.')
            return [False, False]

        # Read out data from file if wished.
        if path:
            try:
                with open(data, 'r') as stream:
                    data = json.load(stream)
                data = json.dumps(data)
            except (OSError, TypeError, ValueError) as e:
                self.logger.error('SERVER | Could not send data. Reason: '
                                  '{}'.format(e))
                return [True, False]

        try:
            # 1. step: Send the length of the message.
            length = len(data)
            self.client_conn.sendall(b'%d\n' % length)
            self.logger.debug('SERVER | Send length of message: {}'.format(
                length))

            # 2. step: Send the original message.
            self.client_conn.sendall(data.encode())
            self.logger.debug('SERVER | Send original message: {}'.format(data))

            self.logger.info('SERVER | Message was sent.')
            return [True, True]
        except socket.error:
            self.logger.error('SERVER | Error, can not send message. Reason: '
                              'No client is connected.')
            return [False, True]

    def recv(self):
        """Receives data from the socket in two steps.
            1. step: Get the length of the message.
            2. step: Receive the original message with respect to step one.

        Special case:
            If a message is received in the JSON format
            {
                "client": "client_name",
                "level": out of {10, 20, 30, 40, 50},
                "msg": "message as string or numeric value"
            }
            then the message is logged with the specified level and client name.

        Return:
            - [#1, #2]
                #1: True if a client is connected, False if not.
                #2: True if the received data was expected, False if not.
        """
        if not self.client_conn:
            self.logger.error('SERVER | Error, can not receive data. Reason: '
                              'No client is connected.')
            return [False, False]

        # Read the length of the data.
        length_str = ""
        char = ""
        while char != '\n':
            length_str += char
            try:
                char = self.client_conn.recv(1).decode()
            except socket.timeout:
                return [True, False]
            except socket.error:
                self.logger.error('SERVER | Error, can not receive data. '
                                  'Reason: No client is connected.')
                return [False, False]
            if not char:
                self.logger.error('SERVER | Error, can not receive data. '
                                  'Reason: No client is connected.')
                return [False, False]
            if (char.isdigit() is False) and (char != '\n'):
                length_str = ""
                char = ""
        total = int(length_str)

        # Receive the data chunk by chunk.
        view = memoryview(bytearray(total))
        next_offset = 0
        while total - next_offset > 0:
            try:
                recv_size = self.client_conn.recv_into(view[next_offset:],
                                                       total - next_offset)
            except socket.timeout:
                return [True, False]
            except socket.error:
                self.logger.error('SERVER | Error, can not receive data. '
                                  'Reason: No client is connected.')
                return [False, False]
            next_offset += recv_size

        data = view.tobytes().decode()

        # If the received message is from a special format, log it with the
        # specified level and client name. Otherwise, log it with level INFO
        # under the name Client.
        data = data.replace("'", '\"')
        client = None
        level = None
        msg = None
        try:
            jmsg = json.loads(data)
            if len(jmsg) == 3:
                client = jmsg['client']
                level = jmsg['level']
                msg = jmsg['msg']
            if level not in range(10, 60, 10):
                level = None
        except (TypeError, KeyError, ValueError):
            pass

        if (client is not None) and (level is not None) and (msg is not None):
            msg = '{} | {}'.format(client, msg)
            self.logger.log(level, msg)
        else:
            if len(data) == 0:
                data = "-- empty string --"
            self.logger.info('Client | {}'.format(data))

        return [True, True]

    def close(self):
        """Closes the socket and the connection to the client."""
        if self.client_conn is not None:
            self.client_conn.close()
            self.client_conn = None
            self.client_addr = None
            self.logger.info('SERVER | Close connection to client.')

        if self.socket is not None:
            self.socket.close()
            self.socket = None
            self.logger.info('SERVER | Close socket.')


class Server(SocketInterface):

    """Connects the user input/ the gui with signals and slots to achieve the
    desired socket communication.
    """

    def __init__(self, count):
        super().__init__(count)
        self.server = SocketServer(self.logger)
        self.last_client_addr = None

        # Threads.
        self.accept_thread = AcceptThread()
        self.accept_thread.server = self.server

        self.receive_thread = ReceiveThread()
        self.receive_thread.server = self.server
        sleep = 1.0
        try:
            sleep = config.var.data['socket']['sleep']
            self.logger.debug('SERVER | Set the sleep time between two '
                              'consecutive messages to {} seconds as defined '
                              'in the config.json file.'.format(sleep))
        except (TypeError, KeyError):
            self.logger.debug('SERVER | Set the sleep time between two '
                              'consecutive messages to the predefined value '
                              'of {}, since no respective entry (socket --> '
                              'sleep) could be find in the config.json file. '
                              'If needed, please make appropriate changes and '
                              'reload this tool.'.format(sleep))
        finally:
            self.receive_thread.sleep = sleep

        self.send_thread = SendThread()
        self.send_thread.server = self.server

        # Connections.
        self.createButton.clicked.connect(self._toggle_server_status)
        self.sendButton.clicked.connect(self._send)
        self.startButton.clicked.connect(self._toggle_recv)
        self.accept_thread.signal.connect(self._enable_start_recv)
        self.send_thread.signal.connect(lambda: self._start_accept("send"))
        self.receive_thread.signal.connect(lambda: self._start_accept("recv"))

    def _toggle_server_status(self):
        """Either starts or stops the server."""
        if self.createButton.isChecked():
            # Starts the server.
            ok = self._create_server()
            if not ok:
                self.createButton.click()
        else:
            # Stops the server
            if self.accept_thread.isRunning():
                self.accept_thread.stop_thread()
                self.accept_thread.wait()

            if self.startButton.isChecked():
                self.startButton.click()
            self.startButton.setEnabled(False)

            if self.send_thread.isRunning():
                self.send_thread.wait()

            self.server.close()

    def _create_server(self):
        """Creates a server and goes into the state of beeing able to accept
         an incoming join request.

        Return:
            - True, if server could be created.
            - False, if not.
        """
        host = self.hostEdit.text()
        try:
            port = int(self.portEdit.text())
        except ValueError:
            self.logger.error('SERVER | Error, the server could not be '
                              'started. Reason: Data type violation. The port '
                              'number has to be provided as an integer.')
            return False
        ok = self.server.create(host, port)
        if ok:
            if self.accept_thread.server is not None:
                self.accept_thread.start()
            else:
                self.logger.critical('Internal error. Server for class '
                                     'AcceptThread is not defined. Please '
                                     'restart the tool.')
                return False
        else:
            return False

        return True

    def _send(self):
        """Sends either a string or the path to a JSON file."""
        if self.stringRadio.isChecked():
            self.send_thread.data = self.stringToSend
            self.send_thread.path = False
            self.send_thread.start()
        else:
            self.send_thread.data = self.fileToSend
            self.send_thread.path = True
            self.send_thread.start()

    def _toggle_recv(self):
        """Starts/Stops receiving messages."""
        if self.startButton.isChecked():
            if self.receive_thread.server is not None:
                self.logger.info('SERVER | Start receiving messages.')

                self.receive_thread.start()
            else:
                self.logger.critical('Internal error. Server for class '
                                     'ReceiveThread is not defined. Please '
                                     'restart the tool.')
        else:
            self.receive_thread.stop_thread()
            self.receive_thread.wait()
            self.logger.info('SERVER | Stop receiving messages.')

    def _enable_start_recv(self):
        """Starts receiving messages after a connection to a client is made."""
        self.last_client_addr = self.server.client_addr
        self.startButton.setEnabled(True)
        self.startButton.click()

    def _start_accept(self, who):
        """Stops receiving messages and starts listening for incoming
        connection requests."""
        if self.startButton.isChecked():
            # Stops receiving messages.
            self.startButton.click()
        if self.createButton.isChecked() \
                and not self.accept_thread.isRunning() \
                and self.last_client_addr == self.server.client_addr:
            # Starts listening for incoming connection requests.
            self.startButton.setEnabled(False)
            self.server.client_conn = None
            self.server.client_addr = None
            self.accept_thread.start()
            self.logger.info('SERVER | Listening for connections.')


class AcceptThread(QThread):

    """A thread for accepting incoming connection requests."""

    signal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.server = None
        self.stop = False

    def __del__(self):
        self.wait()

    def stop_thread(self):
        self.stop = True

    def run(self):
        self.stop = False
        self.server.socket.settimeout(1)
        while True:
            ok = self.server.accept()
            if ok or self.stop:
                break
        self.server.socket.settimeout(None)
        if not self.stop:
            self.signal.emit()


class ReceiveThread(QThread):

    """A thread for fetching messages."""

    signal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.server = None
        self.stop = False

    def __del__(self):
        self.wait()

    def stop_thread(self):
        self.stop = True

    def run(self):
        self.stop = False
        self.server.client_conn.settimeout(1)
        while True:
            time.sleep(0.5)
            ok = self.server.recv()
            if not ok[0] or self.stop:
                break
        self.server.client_conn.settimeout(None)
        if not self.stop:
            self.signal.emit()


class SendThread(QThread):

    """A thread for sending messages."""

    signal = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)
        self.server = None
        self.data = None
        self.path = None

    def __del__(self):
        self.wait()

    def run(self):
        if self.path:
            ok = self.server.send(self.data, path=True)
        else:
            ok = self.server.send(self.data, path=False)
        if not ok[0]:
            self.signal.emit()
