from .utils import BaseInteractable, apply_voltage, get_file, get_number_of_devices
from .constants import offset, __version__
from PyQt6 import QtCore, QtWidgets, QtGui
from .widgets import StepProgressBar
from . import sys_info, settings
from typing import Literal
from .pages import (
    NoSEALKitPage,
    SelectSEALKitPage,
    VoltageOffsetPage,
    ApplyVoltagePage,
    MockedModePage
)

import socket
import logging

logger = logging.getLogger(__name__)


class BasePopup(BaseInteractable, QtWidgets.QDialog):
    def super_(self):
        super().__init__(self.main_window)


class StartUpPopup(BasePopup):
    def __init__(self):
        with self.init():
            self.mocked = False

            self.device_name = None

            system, num_of_devices, drivers = get_number_of_devices(drivers=True)

            self.next_button = QtWidgets.QPushButton('Next')
            self.next_button.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
            self.next_button.setObjectName('next_button')
            self.next_button.setFixedWidth(100)

            self.back_button = QtWidgets.QPushButton('Back')
            self.back_button.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
            self.back_button.setObjectName('back_button')
            self.back_button.setFixedWidth(100)
            self.back_button.hide()

            self.buttons_layout = QtWidgets.QHBoxLayout()
            self.buttons_layout.addWidget(self.back_button)
            self.buttons_layout.addStretch(20)
            self.buttons_layout.addWidget(self.next_button)

            self.stacked_widget = QtWidgets.QStackedWidget()

            self.select_SEAL_kit_page = None

            self.mocked_mode_page = None

            if num_of_devices == 0:
                self.no_SEAL_kit_page = NoSEALKitPage(self, drivers)
                self.total_steps = 4
                self.stacked_widget.addWidget(self.no_SEAL_kit_page)
                self.next_button.hide()
            elif num_of_devices == 1:
                self.device_name = system.devices.device_names[0]
                apply_voltage(self.device_name)
                self.total_steps = 2
            else:
                self.select_SEAL_kit_page = SelectSEALKitPage(self)
                self.stacked_widget.addWidget(self.select_SEAL_kit_page)
                self.total_steps = 3

            self.step_progress_bar = StepProgressBar(self.total_steps)

            self.voltage_offset_page = VoltageOffsetPage(self)

            self.apply_voltage_page = ApplyVoltagePage(self)
            self.stacked_widget.addWidget(self.voltage_offset_page)
            self.stacked_widget.addWidget(self.apply_voltage_page)

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.step_progress_bar)
            self.main_layout.addWidget(self.stacked_widget)
            self.main_layout.addLayout(self.buttons_layout)

        self.main_layout.setContentsMargins(20, 10, 20, 20)
        self.main_layout.setSpacing(0)

        self.setWindowIcon(QtGui.QIcon(get_file('beskar-icon.png')))

        self.setWindowTitle(f'Beskar {__version__}')

        self.setMinimumSize(430, 650)
        self.resize(560, 650)

    def next_page(self, widget: Literal['mocked', 'select', None] = None):
        if self.stacked_widget.currentWidget() == self.voltage_offset_page:
            settings['voltage-offset'] = self.voltage_offset_page.double_spin_box.value()
        self.set_page_index(self.stacked_widget.currentIndex() + 1, widget)

    def set_page_index(self, index: int, widget: Literal['mocked', 'select', None] = None):
        self.step_progress_bar.set_step(index + 1)

        if index == 0:
            self.back_button.hide()
            if self.total_steps == 4:
                self.next_button.hide()
                if (window_title := f'Beskar {__version__}') != self.windowTitle():
                    self.setWindowTitle(window_title)
        else:
            self.back_button.show()
            self.next_button.show()

        if index == len(self.stacked_widget):
            if not self.mocked:
                apply_voltage(
                    self.device_name,
                    (
                        self.voltage_offset_page.double_spin_box.value()
                        + offset - self.apply_voltage_page.double_spin_box.value()
                    )
                )
            settings['applied-voltage'] = self.apply_voltage_page.double_spin_box.value()
            self.accept()
        elif self.total_steps == 4 and index == 1 and widget:
            if widget == 'mocked':
                if not self.mocked_mode_page:
                    self.mocked_mode_page = MockedModePage(self)
                page = self.mocked_mode_page
                other_page = self.select_SEAL_kit_page
                if (window_title := f'Beskar {__version__} (Mocked Mode)') != self.windowTitle():
                    self.setWindowTitle(window_title)
                self.mocked = True
            elif widget == 'select':
                if not self.select_SEAL_kit_page:
                    self.select_SEAL_kit_page = SelectSEALKitPage(self)
                page = self.select_SEAL_kit_page
                other_page = self.mocked_mode_page
                if (window_title := f'Beskar {__version__}') != self.windowTitle():
                    self.setWindowTitle(window_title)
                self.mocked = False
            if self.stacked_widget.widget(1) == other_page:
                self.stacked_widget.removeWidget(other_page)
            if self.stacked_widget.indexOf(page) == -1:
                self.stacked_widget.insertWidget(1, page)
        elif self.stacked_widget.indexOf(self.voltage_offset_page) == index:
            if self.select_SEAL_kit_page:
                self.device_name = self.select_SEAL_kit_page.buttons_group. \
                    checkedButton().text()[1:]
            if not self.voltage_offset_page.set_with_settings:
                self.voltage_offset_page.double_spin_box.setValue(
                    settings.get('voltage-offset', 0)
                )
                self.voltage_offset_page.set_with_settings = True
                if not self.mocked:
                    apply_voltage(self.device_name)
        elif self.stacked_widget.indexOf(self.apply_voltage_page) == index:
            self.apply_voltage_page.set_min_and_max(
                self.voltage_offset_page.double_spin_box.value()
            )
            if not self.apply_voltage_page.set_with_settings:
                settings_applied_voltage = settings.get('applied-voltage', 0)
                if settings_applied_voltage in self.apply_voltage_page:
                    self.apply_voltage_page.double_spin_box.setValue(settings_applied_voltage)
                self.apply_voltage_page.set_with_settings = True

        if index > len(self.stacked_widget) or index < 0:
            logger.warning(
                f'Something attempted to set the stacked widget index to {index}, '
                'which is out of bounds.'
            )
        elif index < len(self.stacked_widget):
            self.stacked_widget.setCurrentIndex(index)
            self.set_focus()

    def set_focus(self):
        self.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)

    @QtCore.pyqtSlot()
    def on_next_button_clicked(self):
        self.next_page()

    @QtCore.pyqtSlot()
    def on_back_button_clicked(self):
        self.set_page_index(self.stacked_widget.currentIndex() - 1)

    def mousePressEvent(self, mouse_event: QtGui.QMouseEvent = None) -> None:
        if hasattr(self.stacked_widget.currentWidget(), 'mouse_press_event'):
            self.stacked_widget.currentWidget().mouse_press_event()
        if ((self.back_button.hasFocus() and not self.back_button.underMouse())
            or (self.next_button.hasFocus() and not self.next_button.underMouse())):
            self.set_focus()
        if mouse_event:
            super().mousePressEvent(mouse_event)

    def show(self):
        super().show()
        self.set_focus()

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        # NOTE: Does not trigger for that many key presses
        if key_event.key() != QtCore.Qt.Key.Key_Escape:
            super().keyPressEvent(key_event)


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

            self.computer_name_label = QtWidgets.QLabel(
                f"<b>Computer Name:</b> {socket.gethostname()}"
            )

            self.sys_info_layout = QtWidgets.QVBoxLayout()
            self.sys_info_layout.addWidget(self.os_name_label)
            self.sys_info_layout.addWidget(self.os_version_label)
            self.sys_info_layout.addWidget(self.os_theme_label)
            self.sys_info_layout.addWidget(self.computer_name_label)

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
                'file a GitHub issue <a style="color: #0078D8; text-decoration: none" '
                'href="https://github.com/Ahsoka/beskar/issues/new">here</a>.'
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
