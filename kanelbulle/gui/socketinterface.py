"""Interface for socket communication."""

import logging
from PyQt5.QtWidgets import (QFileDialog, QGroupBox, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QRadioButton, QStyle,
                             QTextEdit, QVBoxLayout, QWidget)
from kanelbulle.gui.objects import SenderObject
from kanelbulle.gui.widgets import QAutoSizeLineEdit, QVLine
from kanelbulle.utils import log


class SocketInterface(QWidget):

    """Interface for socket communication.

    Arguments:
            stringToSend: The string to send.
            fileToSend: The path to the file to send.
            logger: The logger.
    """

    def __init__(self, count, parent=None):
        """Initializes widgets which are show in groups. Used groups,
        from top to bottom:
            1. settings,
            2. send,
            3. recv.
        """
        super().__init__(parent)
        # Group settings.
        self.hostEdit = self._create_edit("127.0.0.1", 80)
        self.portEdit = self._create_edit("5000", 50)
        self.createButton = QPushButton()
        self.createButton.setCheckable(True)
        self.createButton.setChecked(False)
        self.createButton.clicked.connect(self._toggle_create_server)

        # Group send.
        self.stringToSend = ""
        self.sendEdit = QLineEdit()
        self.sendEdit.textChanged.connect(self._what_to_send)
        self.stringRadio = QRadioButton("Send string.")
        self.stringRadio.setChecked(True)
        self.stringRadio.toggled.connect(self._toggle_radio_data)
        self.jsonRadio = QRadioButton("Send JSON file.")

        self.fileToSend = ""
        self.fileButton = QPushButton()
        self.fileButton.setIcon(self.style().standardIcon(
            getattr(QStyle, "SP_FileIcon")))
        self.fileButton.setToolTip("Open file...")
        self.fileButton.setStatusTip("Open file...")
        self.fileButton.clicked.connect(self._file_open)
        self.sendButton = QPushButton("Send")
        self.sendButton.setToolTip("Send message...")
        self.sendButton.setStatusTip("Send message...")

        # Group recv.
        self.startButton = QPushButton()
        self.startButton.setCheckable(True)
        self.startButton.setChecked(False)
        self.startButton.setEnabled(False)
        self.startButton.clicked.connect(self._toggle_start_recv)

        self.clearButton = QPushButton("Clear")
        self.clearButton.clicked.connect(self.clear)
        self.clearButton.setToolTip("Clear messages...")
        self.clearButton.setStatusTip("Clear messages...")

        self.recvEdit = SocketLog(self)
        self.logger = log.get_logger('Connection {}'.format(count))
        self.logger.addHandler(self.recvEdit)

        # Initialize interface.
        self._toggle_create_server()
        self._toggle_radio_data()
        self._toggle_start_recv()

    @staticmethod
    def _create_edit(text, width):
        """Creates an instance of QAutoSizeLineEdit.

        Args:
            text: The line edit's text.
            width: The minimum width of the widget.

        Return:
            edit: An instance of QAutoSizeLineEdit.
        """
        edit = QAutoSizeLineEdit(min_width=50, max_width=200)
        edit.minWidth = width
        edit.setText(text)
        return edit

    def create_layout(self):
        """Creates a vertical box layout which contains all groups.

        Return:
            layout: The filled vertical box layout.
        """
        layout = QVBoxLayout()
        layout.addWidget(self._group_settings())
        layout.addWidget(self._group_send())
        layout.addWidget(self._group_recv())
        return layout

    def _group_settings(self):
        """Provides a group box frame containing all widgets related to
        settings.

        Return:
            box: The group box frame.
        """
        layout = QHBoxLayout()
        layout.addWidget(QLabel("Host"))
        layout.addWidget(self.hostEdit)
        layout.addWidget(QLabel("Port"))
        layout.addWidget(self.portEdit)
        layout.addWidget(QVLine())
        layout.addWidget(self.createButton)
        layout.addStretch(1)

        box = QGroupBox("Settings")
        box.setLayout(layout)
        return box

    def _group_send(self):
        """Provides a group box frame containing all widgets related to
        sending of messages.

        Return:
            box: The group box frame.
        """
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.stringRadio)
        top_layout.addWidget(self.jsonRadio)
        top_layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.sendEdit)
        bottom_layout.addWidget(self.fileButton)
        bottom_layout.addWidget(QVLine())
        bottom_layout.addWidget(self.sendButton)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        box = QGroupBox("Send message")
        box.setLayout(layout)
        return box

    def _group_recv(self):
        """Provides a group box frame containing all widgets related to
        receiving of messages.

        Return:
            box: The group box frame.
        """
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.startButton)
        top_layout.addWidget(QVLine())
        top_layout.addWidget(self.clearButton)
        top_layout.addStretch()

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.recvEdit.widget)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        box = QGroupBox("Log (received messages)")
        box.setLayout(layout)
        return box

    def _toggle_create_server(self):
        """Toggles between the following states:
            1. Create server.
            2. Stop server.
        """
        if self.createButton.isChecked():
            self.createButton.setText('Stop')
            self.createButton.setToolTip("Stop server...")
            self.createButton.setStatusTip("Stop server...")
        else:
            self.createButton.setText('Create')
            self.createButton.setToolTip("Create server...")
            self.createButton.setStatusTip("Create server...")

    def _toggle_radio_data(self):
        """Toggles between the following options:
            1. Send string.
            2. Send JSON file.
        """
        if self.stringRadio.isChecked():
            self.sendEdit.setDisabled(False)
            self.sendEdit.setPlaceholderText("Type in a string to send.")
            self.fileButton.setDisabled(True)
            self._what_to_send(text=self.stringToSend)
            log.gui.info('Prepared to send a string.')
        else:
            self.stringToSend = self.sendEdit.text()
            self.sendEdit.setDisabled(True)
            self.sendEdit.setPlaceholderText("Select a json file.")
            self.fileButton.setDisabled(False)
            self._what_to_send(text=self.fileToSend)
            log.gui.info('Prepared to send a JSON file.')

    def _toggle_start_recv(self):
        """Toggles between the following states:
            1. Start receiving messages.
            2. Stop receiving messages.
        """
        if self.startButton.isChecked():
            self.startButton.setText('Stop')
            self.startButton.setToolTip("Stop receiving messages...")
            self.startButton.setStatusTip("Stop receiving messages...")
        else:
            self.startButton.setText('Start')
            self.startButton.setToolTip("Start receiving messages...")
            self.startButton.setStatusTip("Start receiving messages...")

    def clear(self):
        """Deletes all the text in the widget."""
        self.recvEdit.widget.clear()
        log.gui.info("Cleared log records in widget.")

    def _what_to_send(self, text):
        """Sets the text of the tool and status tip of sendEdit.

        Args:
            text: The text contained by the tool and status tip.
        """
        if self.stringRadio.isChecked():
            self.stringToSend = text
        self.sendEdit.setText(text)
        self.sendEdit.setToolTip('Send: {}'.format(text))
        self.sendEdit.setStatusTip('Send: {}'.format(text))

    def _file_open(self):
        """Constructs a file dialog to get the path to a JSON file."""
        log.gui.info("Open file dialog to get the path to a JSON file.")
        path, _ = QFileDialog.getOpenFileName(self, "Open file", "",
                                              "JSON files (*.json)")

        if path:
            self.fileToSend = path
            self._what_to_send(text=path)


class SocketLog(logging.Handler):

    """Logging handler which sends the logging output to a widget.

    Attributes:
        widget: The widget responsible for showing the logging output.
        sender: An instance of the class SenderObject, which contains a
        signal used to update the content of the widget. This signal is needed,
        because the used widget belongs to the QtGui class and hence can only
        be accessed from the main thread (here, class MainWindow).
    """

    def __init__(self, parent):
        super().__init__()
        self.setLevel(logging.INFO)
        self.setFormatter(log.FORMATTER)
        self.widget = QTextEdit(parent)
        self.widget.setReadOnly(True)
        self.widget.textChanged.connect(self.scroll)
        self.widget.setPlaceholderText("Create a server and press start to "
                                       "send and receive messages.")
        self.sender = SenderObject()

    def emit(self, record):
        """Updates the content of the widget with new log records."""
        color = log.LOG_LEVEL_COLOR[record.levelname]
        msg = self.format(record)
        msg = '<font color={}> {} </font><br />'.format(color, msg)

        self.sender.signal.emit(self.widget, msg)

    def scroll(self):
        """Scrolls to the bottom of the widget."""
        self.widget.verticalScrollBar().setValue(
            self.widget.verticalScrollBar().maximum())
