from PyQt6 import QtWidgets, QtCore, QtGui


class LinkHoverColorChange(QtWidgets.QLabel):
    def __init__(self, link_color1: str, link_color2: str, *args, **kwargs):
        self.link_color1 = link_color1
        self.link_color2 = link_color2

        self.unformated_text = ''
        if args and isinstance(args[0], str):
            self.unformated_text = args[0]

        super().__init__(*args, **kwargs)

        self.linkHovered.connect(self.change_link_color)

    def setText(self, text: str) -> None:
        self.unformated_text = text
        super().setText(text.format(self.link_color1))

    def _set_formatted_text(self, text: str):
        super().setText(text)

    def change_link_color(self, link):
        if link:
            self._set_formatted_text(self.unformated_text.format(self.link_color2))
            self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        else:
            self._set_formatted_text(self.unformated_text.format(self.link_color1))
            self.unsetCursor()
