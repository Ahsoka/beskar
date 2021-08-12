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

        if self.unformated_text:
            self.setText(self.unformated_text)

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
    def __init__(
        self,
        svg_path: str,
        text: str = '',
        link_color1: str = None,
        link_color2: str = None, indent=20
    ):
        self.text_indent = indent

        self.svg_path = svg_path

        if link_color1 and link_color2:
            self.super = super()
            self.super.__init__(link_color1, link_color2, self.add_indent(text))
        else:
            self.super = super(LinkHoverColorChange, self)
            self.super.__init__(self.add_indent(text))

    def paintEvent(self, paint_event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter()
        painter.begin(self)
        svg_renderer = QtSvg.QSvgRenderer(self.svg_path)
        svg_renderer.setAspectRatioMode(QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        svg_renderer.render(
            painter,
            QtCore.QRectF(3, 3, *(self.get_font_size(),) * 2)
        )
        self.super.paintEvent(paint_event)

    def get_font_size(self):
        font_size = 9 # NOTE: I think the default is 9
        if self.font().pixelSize() != -1:
            font_size = self.font().pixelSize()
        elif self.font().pointSize() != -1:
            font_size = self.font().pointSize()

        return font_size

    def setText(self, text: str) -> None:
        self.super.setText(self.add_indent(text))

    def add_indent(self, text: str) -> str:
        return f'<p style="text-indent: {self.text_indent}px"> ' + text + '</p>'


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
        self.timer.setTimerType(QtCore.Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.repaint)

        self.pen = QtGui.QPen(QtGui.QColorConstants.White, 1)

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )

    def sizeHint(self) -> QtCore.QSize:
        return QtCore.QSize(100, self.bubble_height * 2 + 2)

    def set_step(self, step: int):
        if self.current_step + 1 == step:
            self.timer.start(40)
        else:
            if self.timer.isActive():
                self.timer.stop()
            self.current_step = step
            self.update()

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


class DoubleSpinBox(QtWidgets.QDoubleSpinBox):
    up_clicked = QtCore.pyqtSignal()
    down_clicked = QtCore.pyqtSignal()

    number_keys = {
        QtCore.Qt.Key.Key_0,
        QtCore.Qt.Key.Key_1,
        QtCore.Qt.Key.Key_2,
        QtCore.Qt.Key.Key_3,
        QtCore.Qt.Key.Key_4,
        QtCore.Qt.Key.Key_5,
        QtCore.Qt.Key.Key_6,
        QtCore.Qt.Key.Key_7,
        QtCore.Qt.Key.Key_8,
        QtCore.Qt.Key.Key_9,
    }

    removal_keys = {QtCore.Qt.Key.Key_Backspace, QtCore.Qt.Key.Key_Delete}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.up_clicked.connect(self.remove_highlight)
        self.down_clicked.connect(self.remove_highlight)

        self.valueChanged.connect(self.resize_on_num_change)

    def mousePressEvent(self, mouse_event: QtGui.QMouseEvent):
        # Retrieved from:
        # https://stackoverflow.com/questions/65226231/qspinbox-check-if-up-or-down-button-is-pressed

        super().mousePressEvent(mouse_event)

        opt = QtWidgets.QStyleOptionSpinBox()
        self.initStyleOption(opt)

        control = self.style().hitTestComplexControl(
            QtWidgets.QStyle.ComplexControl.CC_SpinBox,
            opt,
            mouse_event.position().toPoint(),
            self
        )
        if control == QtWidgets.QStyle.SubControl.SC_SpinBoxUp:
            self.up_clicked.emit()
        elif control == QtWidgets.QStyle.SubControl.SC_SpinBoxDown:
            self.down_clicked.emit()

    def remove_highlight(self):
        self.lineEdit().deselect()

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        pre_decimal_len = len(str(int(self.maximum())))
        edit_zone_threshold = pre_decimal_len + self.decimals() + 1
        negative = self.value() < 0 or self.lineEdit().text()[0] == '-'

        cursor_pos = self.lineEdit().cursorPosition()
        text = self.lineEdit().text()
        if negative:
            text = text[1:]
            if cursor_pos != 0:
                cursor_pos -= 1

        if key_event.key() in self.number_keys:
            if cursor_pos < edit_zone_threshold:
                adding = 1

                if cursor_pos == pre_decimal_len:
                    cursor_pos += 1
                try:
                    new_num = float(
                        (
                            text[:cursor_pos]
                            + key_event.text()
                            + text[cursor_pos + 1:]
                        ).rstrip(self.suffix())
                    )
                except ValueError:
                    new_num = float('inf')
                if negative:
                    new_num = -new_num
                if new_num <= self.maximum():
                    minus = ''
                    if negative:
                        minus = '-'
                        adding = 2
                    self.lineEdit().setText(
                        minus + text[:cursor_pos] + key_event.text() + text[cursor_pos + 1:]
                    )

                self.lineEdit().setCursorPosition(cursor_pos + adding)
        elif key_event.key() == QtCore.Qt.Key.Key_Period and cursor_pos == pre_decimal_len:
            self.lineEdit().setCursorPosition(cursor_pos + 1)
        elif key_event.key() in self.removal_keys:
            if cursor_pos > edit_zone_threshold and key_event.key() == QtCore.Qt.Key.Key_Backspace:
                self.lineEdit().setCursorPosition(edit_zone_threshold)
            elif cursor_pos <= edit_zone_threshold:
                new_pos = cursor_pos
                if key_event.key() == QtCore.Qt.Key.Key_Backspace and cursor_pos > 0:
                    if negative and cursor_pos == 1:
                        text = text[1:]
                    else:
                        if cursor_pos == pre_decimal_len + 1:
                            cursor_pos -= 1
                        text = text[:cursor_pos - 1] + '0' + text[cursor_pos:]
                        new_pos = cursor_pos - 1
                elif key_event.key() == QtCore.Qt.Key.Key_Delete and cursor_pos < edit_zone_threshold:
                    if negative and cursor_pos == 0:
                        text = text[1:]
                    else:
                        if cursor_pos == 1:
                            cursor_pos = 2
                        text = text[:cursor_pos] + '0' + text[cursor_pos + 1:]
                        new_pos = cursor_pos + 1
                self.lineEdit().setText(text)
                self.lineEdit().setCursorPosition(new_pos)
        else:
            super().keyPressEvent(key_event)

    def resizeEvent(self, resize_event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(resize_event)
        self.resize(self.sizeHint())

    def resize_on_num_change(self, value):
        size = self.sizeHint()
        if self.size() != size:
            self.resize(size)

    def sizeHint(self) -> QtCore.QSize:
        size_hint = super().sizeHint()
        size = None
        if self.minimum() < 0:
            if self.value() >= 0:
                size = QtCore.QSize(size_hint)
                size.setWidth(size.width() - 5)
        if size is None:
            size = size_hint
        return size
