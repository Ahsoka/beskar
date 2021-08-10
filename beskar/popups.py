from .utils import BaseInteractable, get_file
from PyQt6 import QtCore, QtWidgets, QtGui
from . import sys_info

import logging

logger = logging.getLogger(__name__)


class BasePopup(BaseInteractable, QtWidgets.QDialog):
    def super_(self):
        super().__init__(self.main_window)


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

            self.github_notice = QtWidgets.QLabel(
                "If you don't want to automatically send a crash report please "
                'file a GitHub issue <a href="https://github.com/Ahsoka/beskar/issues/new">here</a>.'
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
