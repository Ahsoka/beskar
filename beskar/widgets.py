from .utils import get_file, get_folder, sort_frames
from PyQt6 import QtWidgets, QtCore, QtGui, QtSvg
from typing import Literal, Union
from .settings import logging_dir
from .logs import setUpLogger

import itertools

logger = setUpLogger(__name__, logging_dir)


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


class StepProgressBar(QtWidgets.QWidget):
    def __init__(
        self,
        steps: Literal[2, 3, 4],
        *args,
        checkmark_icon_dir_str: str = 'images/checkmark-frames',
        **kwargs
    ):
        if steps not in {2, 3, 4}:
            raise TypeError(
                f"StepProgressBar only supports 2, 3, and 4 steps, not '{steps}'"
            )

        super().__init__(*args, **kwargs)

        self.font_size = 8

        self.inter_font = None
        if font_loc := get_file('Inter-Light.ttf', 'fonts'):
            # NOTE: Cannot load the font without fontconfig on macOS
            # and Linux, not sure how to automatically install
            inter_font_id = QtGui.QFontDatabase.addApplicationFont(font_loc)
            if inter_font_id != -1:
                inter_font_name = 'Inter Light'
                inter_font_families = QtGui.QFontDatabase.applicationFontFamilies(
                    inter_font_id
                )
                if inter_font_families:
                    inter_font_name = inter_font_families[0] or inter_font_name

                self.inter_font = QtGui.QFontDatabase.font(
                    inter_font_name, '', self.font_size
                )
            else:
                logger.warning('Failed to load Inter-Light.ttf')

        checkmark_icon_dir = get_folder(checkmark_icon_dir_str)
        self.checkmark_animated = bool(checkmark_icon_dir)
        if self.checkmark_animated:
            self.frames = sort_frames(checkmark_icon_dir, '*.svg')
            self.counter = itertools.cycle(range(8))

        self.checkmark_icon = get_file('checkmark-icon.svg')

        self.total_steps = steps

        self.current_step = 1

        self.bubble_y = 15 + 1
        self.bubble_height = 15
        self.bubble_width = 15

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.repaint)

        self.pen = QtGui.QPen(QtGui.QColorConstants.White, 1)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(100, self.bubble_height * 2 + 2)

    def next_step(self):
        self.timer.start(40)

    def paintEvent(self, paint_event: QtGui.QPaintEvent):
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, on=True)

        if self.inter_font:
            painter.setFont(self.inter_font)
        painter.setPen(self.pen)

        first_bubble_x = 30
        last_bubble_x = paint_event.rect().width() - 30

        self.draw_step_bubble(painter, first_bubble_x, 1)
        self.draw_step_bubble(painter, last_bubble_x, self.total_steps)

        if self.total_steps == 2:
          second_bubble_x = last_bubble_x
        elif self.total_steps == 3 or self.total_steps == 4:
            if self.total_steps == 3:
                second_bubble_x = paint_event.rect().width() / 2
                third_bubble_x = last_bubble_x
            elif self.total_steps == 4:
                midpoint = paint_event.rect().width() - 60
                second_bubble_x = round(midpoint / 3 + 30)
                third_bubble_x = round(2 * midpoint / 3 + 30)

                self.draw_step_bubble(painter, third_bubble_x, 3)

                painter.drawLine(
                    third_bubble_x + self.bubble_width,
                    self.bubble_y,
                    last_bubble_x - self.bubble_width,
                    self.bubble_y
                )

            self.draw_step_bubble(painter, second_bubble_x, 2)

            painter.drawLine(
                second_bubble_x + self.bubble_width,
                self.bubble_y,
                third_bubble_x - self.bubble_width,
                self.bubble_y
            )

        painter.drawLine(
            first_bubble_x + self.bubble_width,
            self.bubble_y,
            second_bubble_x - self.bubble_width,
            self.bubble_y
        )

    def draw_step_bubble(
        self,
        painter: QtGui.QPainter,
        center_x: int,
        number: Union[str, int],
        center_y: int = None,
    ):
        svg_renderer = None

        if center_y is None:
            center_y = self.bubble_y

        if isinstance(number, str):
            number = int(number)

        painter.drawEllipse(
            QtCore.QPoint(center_x, center_y),
            self.bubble_width,
            self.bubble_height
        )

        if number < self.current_step and self.checkmark_icon:
            svg_renderer = QtSvg.QSvgRenderer(self.checkmark_icon)

        if number == self.current_step and self.checkmark_animated and self.timer.isActive():
            frame, counter  = next(self.frames), next(self.counter)
            svg_renderer = QtSvg.QSvgRenderer(str(frame))
            if counter == 7:
                self.timer.stop()
                self.current_step += 1

        if svg_renderer:
            svg_renderer.setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            svg_renderer.render(
                painter,
                QtCore.QRectF(
                    # NOTE: Not sure if this pattern holds with variable font sizes.
                    # Only tested with self.font_size=18
                    center_x - self.bubble_width + self.font_size - 1,
                    self.bubble_y - self.bubble_height + self.font_size - 1,
                    self.font_size * 2,
                    self.font_size * 2
                )
            )
        else:
            painter.drawText(
                center_x - self.font_size / 2 + 1,
                self.font_size / 2 + center_y,
                str(number)
            )

        painter.setPen(self.pen)
