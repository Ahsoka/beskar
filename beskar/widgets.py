from PyQt6 import QtWidgets, QtCore, QtGui, QtSvg


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


class LabelWithIcon(LinkHoverColorChange):
    def __init__(self, svg_path: str, link_color1: str, link_color2: str, *args, **kwargs):
        self.svg_path = svg_path
        super().__init__(link_color1, link_color2, *args, **kwargs)

    def paintEvent(self, paint_event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)
        svg_renderer = QtSvg.QSvgRenderer(self.svg_path)
        svg_renderer.setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        svg_renderer.render(
            painter,
            QtCore.QRectF(3, 3, *(self.font().pixelSize(),) * 2)
        )
        super().paintEvent(paint_event)
