from .popups import MultipleSEALKitsPopup, NoSEALKitPopup, EnterVoltsPopup
from PyQt6 import QtCore, QtGui, QtWidgets
from nidaqmx.system import System

import nidaqmx

class BeskarWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.closing = False

        system = System.local()
        self.enter_volts_popup = EnterVoltsPopup(self)
        if len(system.devices) > 1:
            popup = MultipleSEALKitsPopup(self)
            popup.show()
        elif len(system.devices) == 0:
            popup = NoSEALKitPopup(self)
            popup.show()
        elif len(system.devices) == 1:
            self.device_name = system.devices.device_names[0]
            self.enter_volts_popup.show()

        with nidaqmx.Task() as task:
            task.ao_channels.add_ao_voltage_chan(f'{self.device_name}/ao0', min_val=0, max_val=5)
            task.write(2.5) # Write 2.5 Volts

        # QtCore.QMetaObject.connectSlotsByName(self)

    def closeEvent(self, close_event):
        self.closing = True
