from PyQt6 import QtCore, QtWidgets
from nidaqmx.system import System


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
        self.vertical_layout.addWidget(self.push_button, 0, QtCore.Qt.Alignment.AlignRight)

        self.setLayout(self.vertical_layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot()
    def on_push_button_clicked(self):
         self.parent.device_name = self.combo_box.currentText()
         self.accept()
         self.parent.enter_volts_popup.show()

    def closeEvent(self, close_event):
        if not self.parent.closing:
            new_popup = MultipleSEALKitsPopup(self.parent)
            new_popup.label.setText(
                "You must select which SEAL kit you want to use before starting the program."
            )
            new_popup.show()
