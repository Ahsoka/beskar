from .utils import apply_voltage, get_number_of_devices
from PyQt6 import QtCore, QtWidgets, QtTest
from nidaqmx.system import System
from .constants import offset

import sys
import lorem
import random


class MultipleSEALKitsPopup(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.label = QtWidgets.QLabel(
            "Multiple SEAL kits detected, please selected which one you would like to use:"
        )
        self.label.setObjectName('label')

        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setObjectName('combo_box')
        for device_name in System.local().devices.device_names:
            self.combo_box.addItem(device_name)

        self.push_button = QtWidgets.QPushButton('OK')
        self.push_button.setObjectName('push_button')

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addWidget(self.combo_box)
        self.vertical_layout.addWidget(self.push_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.vertical_layout)

        # self.setWindowFlag(QtCore.Qt.WindowFlags.WindowCloseButtonHint, on=False)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
         self.parent.device_name = self.combo_box.currentText()
         self.accept()
         apply_voltage(self.parent.device_name)
         self.parent.enter_volts_popup.exec()

    def closeEvent(self, close_event):
        sys.exit()


class NoSEALKitPopup(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.label = QtWidgets.QLabel(
            "SEAL kit not detected, please make sure it's plugged in"
        )
        self.label.setObjectName('label')

        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setObjectName('combo_box')

        self.refresh_push_button = QtWidgets.QPushButton('Refresh')
        self.refresh_push_button.setObjectName('refresh_push_button')

        self.mocked_mode_button = QtWidgets.QPushButton('Mocked Mode')
        self.mocked_mode_button.setObjectName('mocked_mode_button')

        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.addWidget(self.refresh_push_button, stretch=10, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.buttons_layout.addWidget(self.mocked_mode_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addLayout(self.buttons_layout)

        self.setLayout(self.vertical_layout)

        # self.setWindowFlag(QtCore.Qt.WindowFlags.WindowCloseButtonHint, on=False)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_refresh_push_button_clicked(self):
        if self.refresh_push_button.text() == 'Refresh':
            self.label.setText('Looking')
            for _ in range(5):
                QtTest.QTest.qWait(100)
                self.label.setText(f"{self.label.text()}.")
            system, num_of_devices = get_number_of_devices()
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
                self.vertical_layout.insertWidget(1, self.combo_box)
                self.refresh_push_button.setText('OK')
        elif self.refresh_push_button.text() == 'OK':
            self.parent.device_name = self.combo_box.currentText()
            self.accept()
            apply_voltage(self.parent.device_name)
            self.parent.enter_volts_popup.exec()
        else:
            raise RuntimeError('This should never be triggered.')

    @QtCore.pyqtSlot()
    def on_mocked_mode_button_clicked(self):
        self.parent.mocked = True
        self.accept()
        self.parent.voltage_offset = round(random.random(), 3)
        if self.parent.settings.get('show-mocked-mode', True):
            mocked_popup = MockedModePopup(self.parent)
            mocked_popup.open()

    def closeEvent(self, close_event):
        sys.exit()


class EnterVoltsPopup(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent
        self.parent.voltage_offset = 0

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

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addLayout(self.middle_horizontal_layout)
        self.vertical_layout.addWidget(self.push_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.vertical_layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
        self.accept()

    @QtCore.pyqtSlot(int)
    def on_horizontal_slider_valueChanged(self, position):
        self.parent.voltage_offset = voltage = position / 1000
        self.double_spin_box.setValue(voltage)
        apply_voltage(self.parent.device_name, voltage + offset)

    @QtCore.pyqtSlot(float)
    def on_double_spin_box_valueChanged(self, value):
        self.parent.voltage_offset = value
        self.horizontal_slider.setValue(int(value * 1000))
        apply_voltage(self.parent.device_name, value + offset)


class MockedModePopup(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.show_again = True

        self.header = QtWidgets.QLabel('<h1>Mocked Mode</h1>')

        self.description = QtWidgets.QLabel(lorem.text())
        self.description.setWordWrap(True)

        self.dont_show_again = QtWidgets.QCheckBox("Don't show this message again.")
        self.dont_show_again.setObjectName('check_box')

        self.ok_button = QtWidgets.QPushButton('OK')
        self.ok_button.setObjectName('ok_button')

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(self.header)
        self.main_layout.addWidget(self.description)
        self.main_layout.addWidget(self.dont_show_again, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.main_layout.addWidget(self.ok_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        self.setLayout(self.main_layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_ok_button_clicked(self):
        self.parent.settings['show-mocked-mode'] = self.show_again
        self.accept()

    @QtCore.pyqtSlot(int)
    def on_check_box_stateChanged(self, state):
        self.show_again = not bool(state)
