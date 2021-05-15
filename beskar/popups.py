from PyQt6 import QtCore, QtWidgets, QtTest
from nidaqmx.system import System
from .utils import apply_voltage
from .constants import offset
from .gui import BeskarWindow


class MultipleSEALKitsPopup(QtWidgets.QDialog):
    def __init__(self, parent: BeskarWindow):
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
        self.vertical_layout.addWidget(self.push_button, 0, QtCore.Qt.Alignment.AlignRight)

        self.setLayout(self.vertical_layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
         self.parent.device_name = self.combo_box.currentText()
         self.accept()
         apply_voltage(self.parent.device_name)
         self.parent.enter_volts_popup.show()

    def closeEvent(self, close_event):
        if not self.parent.closing:
            new_popup = MultipleSEALKitsPopup(self.parent)
            new_popup.label.setText(
                "You must select which SEAL kit you want to use before starting the program."
            )
            new_popup.show()


class NoSEALKitPopup(QtWidgets.QDialog):
    def __init__(self, parent: BeskarWindow):
        super().__init__(parent)

        self.parent = parent

        self.label = QtWidgets.QLabel(
            "SEAL kit not detected, please make sure it's plugged in"
        )
        self.label.setObjectName('label')

        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.setObjectName('combo_box')

        self.push_button = QtWidgets.QPushButton('Refresh')
        self.push_button.setObjectName('push_button')

        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.addWidget(self.label)
        self.vertical_layout.addWidget(self.push_button, 0, QtCore.Qt.Alignment.AlignRight)

        self.setLayout(self.vertical_layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
        if self.push_button.text() == 'Refresh':
            self.label.setText('Looking')
            for _ in range(5):
                QtTest.QTest.qWait(100)
                self.label.setText(f"{self.label.text()}.")
            system = System.local()
            if len(system.devices) == 0:
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
                self.push_button.setText('OK')
        elif self.push_button.text() == 'OK':
            self.parent.device_name = self.combo_box.currentText()
            self.accept()
            apply_voltage(self.parent.device_name)
            self.parent.enter_volts_popup.show()
        else:
            raise RuntimeError('This should never be triggered.')

    def closeEvent(self, close_event):
        if not self.parent.closing:
            new_popup = NoSEALKitPopup(self.parent)
            new_popup.label.setText(
                "You cannot use the progam until the SEAL kit is detected. "
                "Please refresh until it is found."
            )
            new_popup.show()


class EnterVoltsPopup(QtWidgets.QDialog):
    def __init__(self, parent: BeskarWindow):
        super().__init__(parent)

        self.parent = parent

        self.label = QtWidgets.QLabel(
            "Enter current reading on multimeter and "
            "use slider until the reading is zero (or close to zero)"
        )


        self.horizontal_slider = QtWidgets.QSlider(QtCore.Qt.Orientations.Horizontal)
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
        self.vertical_layout.addWidget(self.push_button, 0, QtCore.Qt.Alignment.AlignRight)

        self.setLayout(self.vertical_layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
        self.accept()

    @QtCore.pyqtSlot(int)
    def on_horizontal_slider_valueChanged(self, position):
        self.double_spin_box.setValue(position / 1000)
        apply_voltage(self.parent.device_name, position / 1000 + offset)

    @QtCore.pyqtSlot(float)
    def on_double_spin_box_valueChanged(self, value):
        self.horizontal_slider.setValue(int(value * 1000))
        apply_voltage(self.parent.device_name, value + offset)
