from .popups import MultipleSEALKitsPopup, NoSEALKitPopup, EnterVoltsPopup
from PyQt6 import QtCore, QtGui, QtWidgets
from nidaqmx.system import System
from .utils import apply_voltage


class BeskarWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.closing = False

        system = System.local()
        self.enter_volts_popup = EnterVoltsPopup(self)
        if len(system.devices) > 1:
            popup = MultipleSEALKitsPopup(self)
            popup.exec()
        elif len(system.devices) == 0:
            popup = NoSEALKitPopup(self)
            popup.exec()
        elif len(system.devices) == 1:
            self.device_name = system.devices.device_names[0]
            apply_voltage(self.device_name)
            self.enter_volts_popup.show()

        # QtCore.QMetaObject.connectSlotsByName(self)

    def closeEvent(self, close_event):
        self.closing = True
