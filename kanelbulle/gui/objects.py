"""Useful objects."""

from PyQt5.QtCore import pyqtSignal, QObject


class SenderObject(QObject):

    """Signal with two arguments."""

    signal = pyqtSignal('PyQt_PyObject', 'PyQt_PyObject')
