from .pages import DarkCurrentPage, ScanPage
from PyQt6 import QtCore, QtWidgets, QtGui
from .utils import get_file
from . import __version__
from typing import Union

import os
import logging

logger = logging.getLogger(__name__)

# TODO: Handle event when USB is disconnect in the middle of program


class BeskarWindow(QtWidgets.QMainWindow):
    def __init__(self, mocked: bool, device_name: Union[str, None]):
        super().__init__()

        self.mocked = mocked

        self.device_name = device_name

        self.exiting = False

        self.setWindowTitle(f'Beskar {__version__}')

        icon_path = get_file('beskar-icon.png')
        self.icon = None
        if icon_path:
            self.icon = QtGui.QIcon(icon_path)
            self.setWindowIcon(self.icon)

        self.white_icon =  None

        self.create_options_menu()

        self.dark_current_widget = DarkCurrentPage(self)

        self.scan_widget = ScanPage(self)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.stacked_widget.addWidget(self.dark_current_widget)
        self.stacked_widget.addWidget(self.scan_widget)

        self.main_layout = QtWidgets.QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.menu_widget)
        self.main_layout.addWidget(self.stacked_widget)

        self.layout_widget = QtWidgets.QWidget()
        self.layout_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.layout_widget)

        self.showMaximized()

        QtCore.QMetaObject.connectSlotsByName(self)

    def show(self) -> None:
        # if os.name == 'nt':
        #     # TODO: End thread upon application shutdown

        #     from .update import UpdateChecker, close_toasters
        #     from .handle_errors import handle_exception
        #     from . import app

        #     self.update_thread = UpdateChecker()
        #     self.update_thread.raise_exception.connect(lambda tup: handle_exception(*tup))
        #     self.update_thread.close_all_windows.connect(QtWidgets.QApplication.closeAllWindows)
        #     app.aboutToQuit.connect(close_toasters)
        #     self.update_thread.start()

        super().show()

    def create_options_menu(self):
        space_between_buttons = 20

        self.dark_current_menu = QtWidgets.QCommandLinkButton('Dark Current')
        self.dark_current_menu.setObjectName('dark_current_menu_button')
        self.dark_current_menu.setIcon(QtGui.QIcon(get_file('dark-current-page-icon.svg')))
        self.dark_current_menu.setIconSize(QtCore.QSize(20, 25))
        self.dark_current_menu.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.dark_current_menu.setCheckable(True)
        self.dark_current_menu.setChecked(True)

        self.scan_menu = QtWidgets.QCommandLinkButton('Scan')
        self.scan_menu.setIcon(QtGui.QIcon(get_file('scan-page-icon.svg')))
        self.scan_menu.setIconSize(QtCore.QSize(20, 25))
        self.scan_menu.setObjectName('scan_menu_button')
        self.scan_menu.setCheckable(True)
        self.dark_current_menu.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        self.menu_layout = QtWidgets.QVBoxLayout()
        self.menu_layout.addSpacing(space_between_buttons)
        self.menu_layout.addWidget(self.dark_current_menu)
        self.menu_layout.addSpacing(space_between_buttons)
        self.menu_layout.addWidget(self.scan_menu)
        self.menu_layout.addStretch(40)

        self.menu_widget = QtWidgets.QWidget()
        self.menu_widget.setLayout(self.menu_layout)
        self.menu_widget.setObjectName('menu_widget')

    def closeEvent(self, close_event: QtGui.QCloseEvent) -> None:
        self.exiting = True
        super().closeEvent(close_event)

    @QtCore.pyqtSlot()
    def on_dark_current_menu_button_clicked(self):
        self.dark_current_menu.setChecked(True)
        self.scan_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(0)

        self.dark_current_widget.update_data()

        self.high_dark_current(
            'These dark current values are unusually high values. '
            'There might be something wrong with the SEAL kit you are using.'
        )

    @QtCore.pyqtSlot()
    def on_scan_menu_button_clicked(self):
        self.dark_current_widget.update_data()

        self.scan_menu.setChecked(True)
        self.dark_current_menu.setChecked(False)

        self.stacked_widget.setCurrentIndex(1)

        self.high_dark_current(
            'Scanning may not be accurate due to unusually high dark current values. '
            'There might be something wrong with the SEAL kit you are using.'
        )

    def high_dark_current(self, msg: str, title: str = 'Unusually High Dark Current'):
        if max(self.dark_current_widget.samples) > 1:
            logger.warning('Unusually high dark current detected.')
            QtWidgets.QMessageBox.warning(self, title, msg)
