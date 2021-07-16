from .utils import BaseInteractable, apply_voltage, get_number_of_devices, get_file
from PyQt6 import QtCore, QtWidgets, QtTest, QtGui
from nidaqmx.system import System
from .constants import offset
from . import sys_info

import random
import logging

logger = logging.getLogger(__name__)


class BasePopup(BaseInteractable, QtWidgets.QDialog):
    def super_(self):
        super().__init__(self.main_window)


class MultipleSEALKitsPopup(BasePopup):
    def __init__(self, main_window):
        with self.init(main_window):
            self.label = QtWidgets.QLabel(
                "Multiple SEAL kits detected, please selected which one you would like to use:"
            )
            self.label.setObjectName('label')

            self.combo_box = QtWidgets.QComboBox()
            self.combo_box.setObjectName('combo_box')
            for device_name in System.local().devices.device_names:
                logger.info(f'Detected {device_name}.')
                self.combo_box.addItem(device_name)

            self.ok_button = QtWidgets.QPushButton('OK')
            self.ok_button.setObjectName('ok_button')

            self.quit_button = QtWidgets.QPushButton('Quit')
            self.quit_button.setObjectName('quit_button')

            self.buttons_layout = QtWidgets.QHBoxLayout()
            self.buttons_layout.addWidget(
                self.ok_button,
                stretch=10,
                alignment=QtCore.Qt.AlignmentFlag.AlignRight
            )
            self.buttons_layout.addWidget(
                self.quit_button,
                alignment=QtCore.Qt.AlignmentFlag.AlignRight
            )

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.label)
            self.main_layout.addWidget(self.combo_box)
            self.main_layout.addLayout(self.buttons_layout)

            self.setFixedHeight(95)

            # NOTE: Need to use .connect since for some reason
            # since connectBySlots does not detect the slot
            self.finished.connect(self.finishing)

    @QtCore.pyqtSlot()
    def on_ok_button_clicked(self):
         self.accept()
         logger.info('Accepted MultipleSEALKitPopup via OK button.')

    QtCore.pyqtSlot()
    def on_quit_button_clicked(self):
        self.main_window.exiting = True
        self.reject()
        logger.info('Rejected MultipleSEALKitPopup via quit button.')
        QtCore.QCoreApplication.quit()

    def finishing(self, result):
        if not self.main_window.exiting:
            self.main_window.device_name = self.combo_box.currentText()
            logger.info(f'Selected {self.main_window.device_name} as the SEAL kit.')
            apply_voltage(self.main_window.device_name)
            self.main_window.enter_volts_popup.open()
            logger.info('EnterVoltsPopup opened from MultipleSEALKitPopup.')


class NoSEALKitPopup(BasePopup):
    def __init__(self, main_window):
        with self.init(main_window):
            self.label = QtWidgets.QLabel(
                "SEAL kit not detected, please make sure it's plugged in"
            )

            self.no_drivers = QtWidgets.QLabel(
                '<b>WARNING:</b> Drivers are not detected on this computer. '
                'In order to connect with the SEAL kit you must install the drivers from '
                '<a href="https://www.ni.com/en-us/support/downloads/drivers/download.ni-daqmx.html#348669">here</a>.'
            )
            self.no_drivers.setOpenExternalLinks(True)
            self.no_drivers.setWordWrap(True)
            self.no_drivers.hide()

            self.combo_box = QtWidgets.QComboBox()
            self.combo_box.setObjectName('combo_box')

            self.refresh_push_button = QtWidgets.QPushButton('Refresh')
            self.refresh_push_button.setObjectName('refresh_push_button')

            self.mocked_mode_button = QtWidgets.QPushButton('Mocked Mode')
            self.mocked_mode_button.setObjectName('mocked_mode_button')

            self.quit_button = QtWidgets.QPushButton('Quit')
            self.quit_button.setObjectName('quit_button')

            self.buttons_layout = QtWidgets.QHBoxLayout()
            self.buttons_layout.addWidget(self.refresh_push_button)
            self.buttons_layout.addWidget(self.mocked_mode_button)
            self.buttons_layout.addWidget(self.quit_button)

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.label)
            self.main_layout.addWidget(self.no_drivers)
            self.main_layout.addLayout(self.buttons_layout)

            self.setWindowFlag(QtCore.Qt.WindowType.WindowCloseButtonHint, on=False)

            self.setFixedSize(315, 68)

    @QtCore.pyqtSlot()
    def on_refresh_push_button_clicked(self):
        if self.refresh_push_button.text() == 'Refresh':
            self.label.setText('Looking')
            for _ in range(5):
                QtTest.QTest.qWait(100)
                self.label.setText(f"{self.label.text()}.")
            system, num_of_devices, has_drivers = get_number_of_devices(drivers=True)
            if not has_drivers and self.no_drivers.isHidden():
                logger.warning('No drivers detected.')
                self.setFixedHeight(130)
                self.no_drivers.show()
            if num_of_devices == 0:
                self.label.setText('SEAL kit not detected, please try refreshing again.')
            else:
                for device_name in system.devices.device_names:
                    self.combo_box.addItem(device_name)
                if len(system.devices.device_names) == 1:
                    self.label.setText("The SEAL kit has been detected! Click 'OK' to access the program.")
                else:
                    self.label.setText(
                        "Several SEAL kits have been detected. Please select which one you would like to use and click 'OK'."
                    )
                self.main_layout.insertWidget(1, self.combo_box)
                self.refresh_push_button.setText('OK')
        elif self.refresh_push_button.text() == 'OK':
            self.main_window.device_name = self.combo_box.currentText()
            self.accept()
            apply_voltage(self.main_window.device_name)
            self.main_window.enter_volts_popup.open()
            logger.info('EnterVoltsPopup opened from NoSEALKitPopup.')
        else:
            raise RuntimeError('This should never be triggered.')

    def keyPressEvent(self, key_event: QtGui.QKeyEvent) -> None:
        if key_event.key() != QtCore.Qt.Key.Key_Escape:
            super().keyPressEvent(key_event)

    @QtCore.pyqtSlot()
    def on_mocked_mode_button_clicked(self):
        self.main_window.mocked = True
        logger.info('Mocked mode activated.')
        self.accept()
        self.main_window.voltage_offset = round(random.random(), 3)
        self.main_window.apply_voltage_widget.set_min_and_max()
        if self.main_window.settings.get('show-mocked-mode', True):
            mocked_popup = MockedModePopup(self.main_window)
            mocked_popup.open()
            logger.info('MockedModePopup opened from NoSEALKitPopup.')

    @QtCore.pyqtSlot()
    def on_quit_button_clicked(self):
        self.reject()
        logger.info('Rejected NoSEALKitPopup via quit button.')
        QtCore.QCoreApplication.quit()


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

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
        self.main_window.settings['voltage-offset'] = self.main_window.voltage_offset
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
        self.double_spin_box.setValue(self.main_window.settings.get('voltage-offset', 0))
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

    def closeEvent(self, close_event):
        self.main_window.settings['show-mocked-mode'] = self.show_again

    @QtCore.pyqtSlot()
    def on_ok_button_clicked(self):
        self.main_window.settings['show-mocked-mode'] = self.show_again
        self.accept()
        logger.info('Accepted MockedModePopup via OK button.')

    @QtCore.pyqtSlot(int)
    def on_check_box_stateChanged(self, state):
        self.show_again = not bool(state)


class ErrorPopup(BasePopup):
    def __init__(self, main_window, traceback: str):
        with self.init(main_window):
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

            self.close_button = QtWidgets.QPushButton('Close')
            self.close_button.setObjectName('close_button')

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.addWidget(self.uh_oh_label)
            self.main_layout.addWidget(self.sys_info_group_box)
            self.main_layout.addWidget(self.error_traceback_group_box)
            self.main_layout.addWidget(self.dont_send_crash_report)
            self.main_layout.addWidget(
                self.close_button,
                alignment=QtCore.Qt.AlignmentFlag.AlignRight
            )

            self.setWindowTitle('Crash Report')

    @QtCore.pyqtSlot()
    def on_close_button_clicked(self):
        self.accept()
        logger.info('ErrorPopup accepted via Close button.')

    @QtCore.pyqtSlot(int)
    def on_dont_send_crash_button_stateChanged(self, state):
        self.sending = not bool(state)
