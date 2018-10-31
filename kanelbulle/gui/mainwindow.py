"""The main window of kanelbulle."""

from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import (QAction, QMainWindow, QStatusBar, QTabWidget,
                             QVBoxLayout, QWidget)
from kanelbulle.misc.socket import Server
from kanelbulle.utils import log


class MainWindow(QMainWindow):

    """The main window of kanelbulle.

    Adds all needed components to a vbox, initializes sub-widgets,
    and connects signals.

    Attributes:
        count: Number of total connections.
        status: The status bar widget.
        tabs: List of all added widgets to tabwidget.
        tabwidget: The tab widget.
    """

    def __init__(self, parent=None):
        """Creates a new main window."""
        super().__init__(parent)
        # Set the size of the main window.
        self.setMinimumWidth(700)

        # Define tab environment.
        self.tabs = list()
        self.count = 0
        self.tabwidget = QTabWidget()

        # Define menu-bar.
        edit_menu = self.menuBar().addMenu("&Edit")
        self._create_action(edit_menu, "New connection", self._add_tab)
        self._create_action(edit_menu, "Close current connection",
                            self._close_tab)

        # Set layout.
        layout = QVBoxLayout()
        layout.addWidget(self.tabwidget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set status bar.
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Initial tab.
        self._add_tab()

    def _create_action(self, menu, desc, slot):
        """Creates an user interface action and adds it to a menu bar.

        Args:
            menu: The menu bar widget.
            desc: The description of the action.
            slot: The slot, which is triggered by the action.
        """
        action = QAction(desc, self)
        action.setStatusTip(desc + "...")
        action.triggered.connect(slot)
        menu.addAction(action)

    def _add_tab(self):
        """Adds a new connection (tab)."""
        self.count += 1
        log.gui.info('Add connection {}'.format(self.count))

        # The tabbed widget.
        server = Server(self.count)
        server.recvEdit.sender.signal.connect(self._update_socket_log)
        layout = QVBoxLayout()
        layout.addLayout(server.create_layout())
        tab = QWidget()
        tab.setLayout(layout)

        # Remember the tabbed widget.
        self.tabs.append([server, tab])

        # Add the tabbed widget to the tab widget and show it.
        self.tabwidget.addTab(tab, "Connection {}".format(self.count))
        self.tabwidget.setCurrentIndex(self.count-1)

    def _close_tab(self):
        """Closes the current visible connection (tab) and deletes the
        respective sub-widget."""
        idx = self.tabwidget.currentIndex()

        # Close the server connection of the active tab.
        server = self.tabs[idx][0]
        if server.createButton.isChecked():
            server.createButton.click()

        # Remove the tabbed widget from the tab widget.
        self.tabwidget.removeTab(idx)

        # Delete the tabbed widget.
        tab = self.tabs[idx][1]
        tab.deleteLater()

        # Remove the list entry of the tabbed widget.
        self.tabs.pop(idx)

        log.gui.info('Deleted connection {}'.format(self.count))

    def _update_socket_log(self, widget, msg):
        """Inserts html formatted text at the end of widget.

        Args:
            widget: An instance of QTextEdit.
            msg: The html formatted text do display.
        """
        widget.moveCursor(QTextCursor.End)
        widget.insertHtml(msg)
