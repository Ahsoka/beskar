from .popups import MultipleSEALKitsPopup, NoSEALKitPopup, EnterVoltsPopup
from .utils import apply_voltage, get_file, get_number_of_devices
from .pages import ApplyVoltagePage, DarkCurrentPage, ScanPage
from .update import UpdateChecker, close_toasters
from PySide6 import QtCore, QtWidgets, QtGui
from . import __version__

import os
import logging

logger = logging.getLogger(__name__)


class BeskarWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.mocked = False

        self.device_name = None

        self.exiting = False

        self.setWindowTitle(f'Beskar {__version__}')

        icon_path = get_file('beskar-icon.png')
        self.icon = None
        if icon_path:
            self.icon = QtGui.QIcon(icon_path)
            self.setWindowIcon(self.icon)

        self.white_icon =  None

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

    def show(self) -> None:
        if os.name == 'nt':
            from .handle_errors import handle_exception
            from . import app

            self.update_thread = UpdateChecker()
            self.update_thread.raise_exception.connect(lambda tup: handle_exception(*tup))
            self.update_thread.close_all_windows.connect(QtWidgets.QApplication.closeAllWindows)
            app.aboutToQuit.connect(close_toasters)
            self.update_thread.start()

        system, num_of_devices = get_number_of_devices()
        self.enter_volts_popup = EnterVoltsPopup(self)
        if num_of_devices > 1:
            popup = MultipleSEALKitsPopup(self)
            popup.open()
            logger.info('Opened MultipleSEALKitPopup from BeskarWindow.')
        elif num_of_devices == 0:
            popup = NoSEALKitPopup(self)
            popup.open()
            logger.info('Opened NoSEALKitPopup from BeskarWindow.')
        elif num_of_devices == 1:
            self.device_name = system.devices.device_names[0]
            apply_voltage(self.device_name)
            self.enter_volts_popup.open()
            logger.info('Opened EnterVoltsPopup from BeskarWindow.')

        super().show()

    def create_options_menu(self):
        space_between_buttons = 20

        # TODO: Add description for each QCommandLinkButton
        self.apply_voltage_menu = QtWidgets.QCommandLinkButton('Apply Voltage')
        # self.apply_voltage_menu.setIcon(QtGui.QIcon(r'C:\Users\AA12 Louqe\Downloads\thunderbolt.svg'))
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

    def closeEvent(self, close_event: QtGui.QCloseEvent) -> None:
        self.exiting = True
        super().closeEvent(close_event)

    @QtCore.Slot()
    def on_apply_voltage_menu_button_clicked(self):
        self.apply_voltage_menu.setChecked(True)
        self.dark_current_menu.setChecked(False)
        self.scan_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(0)

    @QtCore.Slot()
    def on_dark_current_menu_button_clicked(self):
        self.dark_current_menu.setChecked(True)
        self.apply_voltage_menu.setChecked(False)
        self.scan_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(1)

        self.dark_current_widget.update_data()

        self.high_dark_current(
            'These dark current values are unusually high values. '
            'There might be something wrong with the SEAL kit you are using.'
        )

    @QtCore.Slot()
    def on_scan_menu_button_clicked(self):
        self.dark_current_widget.update_data()

        self.scan_menu.setChecked(True)
        self.apply_voltage_menu.setChecked(False)
        self.dark_current_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(2)

        self.high_dark_current(
            'Scanning may not be accurate due to unusually high dark current values. '
            'There might be something wrong with the SEAL kit you are using.'
        )

    def high_dark_current(self, msg: str, title: str = 'Unusually High Dark Current'):
        if max(self.dark_current_widget.samples) > 1:
            logger.warning('Unusually high dark current detected.')
            QtWidgets.QMessageBox.warning(self, title, msg)
