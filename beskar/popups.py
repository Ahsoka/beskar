from .utils import BaseInteractable, apply_voltage, get_file
from PyQt6 import QtCore, QtWidgets, QtGui
from . import sys_info, settings
from .constants import offset

import logging

logger = logging.getLogger(__name__)


class BasePopup(BaseInteractable, QtWidgets.QDialog):
    def super_(self):
        super().__init__(self.main_window)


class EnterVoltsPopup(BasePopup):
    def __init__(self, main_window):
        with self.init(main_window):
            self.main_window.voltage_offset = 0

            self.label = QtWidgets.QLabel(
                "Enter current reading on multimeter and "
                "use slider until the reading is zero (or close to zero)"
            )


            self.horizontal_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            self.horizontal_slider.setObjectName('horizontal_slider')
            self.horizontal_slider.setMaximum(1000)

            self.double_spin_box = QtWidgets.QDoubleSpinBox()
            self.double_spin_box.setObjectName('double_spin_box')
            self.double_spin_box.setRange(0, 1)
            self.double_spin_box.setSingleStep(0.001)
            self.double_spin_box.setDecimals(3)
            self.double_spin_box.setSuffix(' Volts')

            self.middle_horizontal_layout = QtWidgets.QHBoxLayout()
            self.middle_horizontal_layout.addWidget(self.horizontal_slider)
            self.middle_horizontal_layout.addWidget(self.double_spin_box)


            self.push_button = QtWidgets.QPushButton('OK')
            self.push_button.setObjectName('push_button')

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.label)
            self.main_layout.addLayout(self.middle_horizontal_layout)
            self.main_layout.addWidget(self.push_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

            self.setWindowTitle('Select Offset Voltage')

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
        settings['voltage-offset'] = self.main_window.voltage_offset
        self.main_window.apply_voltage_widget.set_min_and_max()
        self.accept()
        logger.info('Accepted EnterVoltsPopup via OK button.')

    @QtCore.pyqtSlot(int)
    def on_horizontal_slider_valueChanged(self, position):
        self.main_window.voltage_offset = voltage = position / 1000
        self.double_spin_box.setValue(voltage)
        apply_voltage(self.main_window.device_name, voltage + offset)

    @QtCore.pyqtSlot(float)
    def on_double_spin_box_valueChanged(self, value):
        self.main_window.voltage_offset = value
        self.horizontal_slider.setValue(int(value * 1000))
        apply_voltage(self.main_window.device_name, value + offset)

    def open(self):
        self.double_spin_box.setValue(settings.get('voltage-offset', 0))
        return super().open()

    def closeEvent(self, close_event):
        self.main_window.apply_voltage_widget.set_min_and_max()


class MockedModePopup(BasePopup):
    def __init__(self, main_window):
        with self.init(main_window):
            self.show_again = True

            self.setFixedSize(350, 225)

            # NOTE: This file must exist or the program will crash
            with get_file('mocked-mode.md', 'desc', path=True).open() as file:
                self.text = QtWidgets.QLabel(file.read())
                self.text.setWordWrap(True)
                self.text.setTextFormat(QtCore.Qt.TextFormat.RichText)

            self.dont_show_again = QtWidgets.QCheckBox("Don't show this message again.")
            self.dont_show_again.setObjectName('check_box')

            self.ok_button = QtWidgets.QPushButton('OK')
            self.ok_button.setObjectName('ok_button')

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.text)
            self.main_layout.addWidget(self.dont_show_again, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            self.main_layout.addWidget(self.ok_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            self.setWindowTitle('Mocked Mode')

    def closeEvent(self, close_event):
        settings['show-mocked-mode'] = self.show_again

    @QtCore.pyqtSlot()
    def on_ok_button_clicked(self):
        settings['show-mocked-mode'] = self.show_again
        self.accept()
        logger.info('Accepted MockedModePopup via OK button.')

    @QtCore.pyqtSlot(int)
    def on_check_box_stateChanged(self, state):
        self.show_again = not bool(state)


class ErrorPopup(BasePopup):
    def __init__(self, traceback: str):
        with self.init():
            self.sending = True

            self.uh_oh_label = QtWidgets.QLabel(
                '<b>Uh oh. A fatal error has occured in Beskar.</b><br>'
                'The following information will be sent in crash report to the developer.'
            )

            self.os_name_label = QtWidgets.QLabel(
                f"<b>OS Name:</b> {sys_info['name']}"
            )

            self.os_version_label = QtWidgets.QLabel(
                f"<b>OS Version:</b> {sys_info['version']}"
            )

            self.os_theme_label = QtWidgets.QLabel(
                f"<b>OS Theme:</b> {sys_info['theme']}"
            )

            self.sys_info_layout = QtWidgets.QVBoxLayout()
            self.sys_info_layout.addWidget(self.os_name_label)
            self.sys_info_layout.addWidget(self.os_version_label)
            self.sys_info_layout.addWidget(self.os_theme_label)

            self.sys_info_group_box = QtWidgets.QGroupBox('System Information')
            self.sys_info_group_box.setLayout(self.sys_info_layout)

            self.error_traceback = QtWidgets.QPlainTextEdit(traceback)
            self.error_traceback.setReadOnly(True)

            self.error_traceback_layout = QtWidgets.QVBoxLayout()
            self.error_traceback_layout.addWidget(self.error_traceback)

            self.error_traceback_group_box = QtWidgets.QGroupBox('Error Traceback')
            self.error_traceback_group_box.setLayout(self.error_traceback_layout)

            self.dont_send_crash_report = QtWidgets.QCheckBox(
                "Don't send crash report."
            )
            self.dont_send_crash_report.setObjectName('dont_send_crash_button')

            self.github_notice = QtWidgets.QLabel(
                "If you don't want to automatically send a crash report please "
                'file a GitHub issue <a href="https://github.com/Ahsoka/beskar/issues/new">here</a>.'
            )
            self.github_notice.setOpenExternalLinks(True)

            self.close_button = QtWidgets.QPushButton('Close')
            self.close_button.setObjectName('close_button')

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.uh_oh_label)
            self.main_layout.addWidget(self.sys_info_group_box)
            self.main_layout.addWidget(self.error_traceback_group_box)
            self.main_layout.addWidget(self.github_notice)
            self.main_layout.addWidget(self.dont_send_crash_report)
            self.main_layout.addWidget(
                self.close_button,
                alignment=QtCore.Qt.AlignmentFlag.AlignRight
            )

            icon_path = get_file('warning.png')
            # Icon attribution: https://www.flaticon.com/authors/gregor-cresnar
            if icon_path:
                self.setWindowIcon(QtGui.QIcon(icon_path))

            self.setWindowTitle('Crash Report')

    @QtCore.pyqtSlot()
    def on_close_button_clicked(self):
        self.accept()
        logger.info('ErrorPopup accepted via Close button.')

    @QtCore.pyqtSlot(int)
    def on_dont_send_crash_button_stateChanged(self, state):
        self.sending = not bool(state)

    def showEvent(self, show_event: QtGui.QShowEvent) -> None:
        self.activateWindow()
        super().showEvent(show_event)
