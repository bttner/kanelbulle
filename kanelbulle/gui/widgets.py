"""Useful widgets."""

from PyQt5.QtWidgets import QFrame, QLineEdit


class QHLine(QFrame):

    """Horizontal frame."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class QVLine(QFrame):

    """Vertical frame."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.VLine)
        self.setFrameShadow(QFrame.Sunken)


class QAutoSizeLineEdit(QLineEdit):

    """A QLineEdit widget which automatically adjusts his width w to the input
    with respect to the bounds minWidth < w < maxWidth.

    Attributes:
        minWidth: Lower bound for width.
        maxWidth: Upper bound for width.
    """

    def __init__(self, min_width, max_width, parent=None):
        super().__init__(parent)
        self.minWidth = min_width
        self.maxWidth = max_width
        self.textChanged.connect(self.adjust_width)

    def adjust_width(self):
        """Adjust the width with respect to the bounds."""
        fm = self.fontMetrics()
        width = fm.width(self.text())+10
        if width < self.minWidth:
            width = self.minWidth
        elif width > self.maxWidth:
            width = self.maxWidth
        self.setFixedWidth(width)
