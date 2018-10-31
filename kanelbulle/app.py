"""Initialize and run kanelbulle."""

import sys
from PyQt5.QtWidgets import QApplication
from kanelbulle.config import config
from kanelbulle.utils import log
from kanelbulle.gui import mainwindow


app = None


def main():
    """Initialize and run the application."""
    global app
    app = QApplication(sys.argv)
    app.setApplicationName("kanelbulle")

    initialization()

    window = mainwindow.MainWindow()
    window.show()

    return mainloop()


def initialization():
    """Initialization routine."""
    log.__init__()
    log.log.info("Log file initialized.")
    if config.var.data is None:
        log.config.warning("{}.".format(config.var.error))
    if log.ERROR:
        log.log.warning('Could not find settings in config.')


def mainloop():
    """Simple wrapper to get a better stack trace for segfaults."""
    return app.exec_()
