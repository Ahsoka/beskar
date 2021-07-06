from .popups import MultipleSEALKitsPopup, NoSEALKitPopup, EnterVoltsPopup
from .pages import ApplyVoltagePage, DarkCurrentPage, ScanPage
from .utils import apply_voltage, get_number_of_devices
from PyQt6 import QtCore, QtWidgets, QtGui
from .settings import Settings
from . import __version__

import pathlib


class BeskarWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.mocked = False

        self.settings = Settings()

        self.setWindowTitle(f'Beskar {__version__}')

        try:
            icon_path = next(pathlib.Path('.').glob('**/images/beskar-icon.png'))
            self.setWindowIcon(QtGui.QIcon(str(icon_path)))
        except StopIteration:
            # If this happens, somehow the icon was deleted from the install folder
            # TODO: Connect to internet and reinstall icon
            pass

        system, num_of_devices = get_number_of_devices()
        self.enter_volts_popup = EnterVoltsPopup(self)
        if num_of_devices > 1:
            popup = MultipleSEALKitsPopup(self)
            popup.exec()
        elif num_of_devices == 0:
            popup = NoSEALKitPopup(self)
            popup.exec()
        elif num_of_devices == 1:
            self.device_name = system.devices.device_names[0]
            apply_voltage(self.device_name)
            self.enter_volts_popup.exec()

        self.create_options_menu()

        self.apply_voltage_widget = ApplyVoltagePage(self)

        self.dark_current_widget = DarkCurrentPage(self)

        self.scan_widget = ScanPage(self)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.stacked_widget.addWidget(self.apply_voltage_widget)
        self.stacked_widget.addWidget(self.dark_current_widget)
        self.stacked_widget.addWidget(self.scan_widget)

        self.splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.menu_group_box)
        self.splitter.addWidget(self.stacked_widget)

        self.setCentralWidget(self.splitter)
        self.splitter.setSizes((1, 100_000))
        self.showMaximized()

        QtCore.QMetaObject.connectSlotsByName(self)

    def create_options_menu(self):
        space_between_buttons = 20

        # TODO: Add description for each QCommandLinkButton
        self.apply_voltage_menu = QtWidgets.QCommandLinkButton('Apply Voltage')
        self.apply_voltage_menu.setObjectName('apply_voltage_menu_button')
        self.apply_voltage_menu.setCheckable(True)
        self.apply_voltage_menu.setChecked(True)

        spacer1 = QtWidgets.QSpacerItem(
            0, space_between_buttons, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred
        )

        self.dark_current_menu = QtWidgets.QCommandLinkButton('Dark Current')
        self.dark_current_menu.setObjectName('dark_current_menu_button')
        self.dark_current_menu.setCheckable(True)

        spacer2 = QtWidgets.QSpacerItem(
            0, space_between_buttons, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred
        )

        self.scan_menu = QtWidgets.QCommandLinkButton('Scan')
        self.scan_menu.setObjectName('scan_menu_button')
        self.scan_menu.setCheckable(True)

        spacer3 = QtWidgets.QSpacerItem(
            0, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.vertical_menu_layout = QtWidgets.QVBoxLayout()
        self.vertical_menu_layout.addWidget(self.apply_voltage_menu)
        self.vertical_menu_layout.addItem(spacer1)
        self.vertical_menu_layout.addWidget(self.dark_current_menu)
        self.vertical_menu_layout.addItem(spacer2)
        self.vertical_menu_layout.addWidget(self.scan_menu)
        self.vertical_menu_layout.addItem(spacer3)

        self.menu_group_box = QtWidgets.QGroupBox()
        self.menu_group_box.setLayout(self.vertical_menu_layout)

    @QtCore.pyqtSlot()
    def on_apply_voltage_menu_button_clicked(self):
        self.apply_voltage_menu.setChecked(True)
        self.dark_current_menu.setChecked(False)
        self.scan_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_dark_current_menu_button_clicked(self):
        self.dark_current_menu.setChecked(True)
        self.apply_voltage_menu.setChecked(False)
        self.scan_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(1)

        self.dark_current_widget.update_data()

        if max(self.dark_current_widget.samples) > 1:
            QtWidgets.QMessageBox.warning(
                self,
                'Unusually High Dark Current',
                'These dark current values are unusually high values.'
                ' There might be something wrong with the SEAL kit you are using.'
            )

    @QtCore.pyqtSlot()
    def on_scan_menu_button_clicked(self):
        self.scan_menu.setChecked(True)
        self.apply_voltage_menu.setChecked(False)
        self.dark_current_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(2)

        if max(self.dark_current_widget.samples) > 1:
             QtWidgets.QMessageBox.warning(
                self,
                'Unusually High Dark Current',
                'Scanning may not be accurate due to unusually high dark current values. '
                'There might be something wrong with the SEAL kit your using.'
            )
