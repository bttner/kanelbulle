"""Initialize and run kanelbulle."""

import sys
from PyQt5.QtWidgets import QApplication
from kanelbulle.gui import mainwindow

app = None


def main():
    """Initialize and run the application."""
    global app
    app = QApplication(sys.argv)
    app.setApplicationName("kanelbulle")

    window = mainwindow.MainWindow()
    window.show()

    return mainloop()


def mainloop():
    """Simple wrapper to get a better stack trace for segfaults."""
    return app.exec_()
