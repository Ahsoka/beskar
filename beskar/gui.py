from .popups import MultipleSEALKitsPopup, NoSEALKitPopup, EnterVoltsPopup
from PyQt6 import QtCore, QtGui, QtWidgets
from nidaqmx.system import System
from .constants import h1_font, offset
from .utils import apply_voltage

import lorem


class BeskarWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.closing = False
        self.current_voltage_applied = 0

        self.create_options_menu()

        self.create_apply_voltage_page()

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientations.Horizontal)
        splitter.addWidget(self.menu_group_box)
        apply_voltage_layout_widget = QtWidgets.QWidget()
        apply_voltage_layout_widget.setLayout(self.apply_voltage_layout)
        splitter.addWidget(apply_voltage_layout_widget)

        self.main_layout = QtWidgets.QHBoxLayout()
        # self.main_layout.setContentsMargins()
        self.main_layout.addWidget(splitter)

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
            self.enter_volts_popup.open()


        self.setLayout(self.main_layout)
        self.showMaximized()
        splitter.setSizes((1, 100_000))

        QtCore.QMetaObject.connectSlotsByName(self)

    def create_options_menu(self):
        space_between_buttons = 20

        # TODO: Add description for each QCommandLinkButton
        self.apply_voltage_menu = QtWidgets.QCommandLinkButton('Apply Voltage')
        self.apply_voltage_menu.setCheckable(True)
        self.apply_voltage_menu.setChecked(True)

        spacer1 = QtWidgets.QSpacerItem(
            0, space_between_buttons, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred
        )

        self.dark_current_menu = QtWidgets.QCommandLinkButton('Dark Current')
        self.dark_current_menu.setCheckable(True)

        spacer2 = QtWidgets.QSpacerItem(
            0, space_between_buttons, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Preferred
        )

        self.scan_menu = QtWidgets.QCommandLinkButton('Scan')
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

    def create_apply_voltage_page(self):
        self.apply_voltage_label = QtWidgets.QLabel("Apply Voltage")
        self.apply_voltage_label.setFont(h1_font)

        spacer1 = QtWidgets.QSpacerItem(
            0, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.apply_voltage_horizontal_slider = QtWidgets.QSlider(QtCore.Qt.Orientations.Horizontal)
        self.apply_voltage_horizontal_slider.setObjectName('apply_voltage_horizontal_slider')
        self.apply_voltage_horizontal_slider.setMaximum(1000)
        self.apply_voltage_horizontal_slider.setValue(500)

        self.apply_voltage_spin_box = QtWidgets.QDoubleSpinBox()
        self.apply_voltage_spin_box.setObjectName('apply_voltage_spin_box')
        self.apply_voltage_spin_box.setRange(-5, 5)
        self.apply_voltage_spin_box.setSingleStep(0.01)
        self.apply_voltage_spin_box.setSuffix(' Volts')

        self.apply_voltage_button = QtWidgets.QPushButton('Apply')
        self.apply_voltage_button.setObjectName('apply_voltage_button')
        self.apply_voltage_button.setEnabled(False)

        interaction_hbox = QtWidgets.QHBoxLayout()
        interaction_hbox.addWidget(self.apply_voltage_horizontal_slider)
        interaction_hbox.addWidget(self.apply_voltage_spin_box)

        self.main_apply_voltage_layout = QtWidgets.QVBoxLayout()
        self.main_apply_voltage_layout.contentsMargins().setLeft(1000)
        self.main_apply_voltage_layout.contentsMargins().setRight(1000)
        self.main_apply_voltage_layout.setContentsMargins(
            self.main_apply_voltage_layout.contentsMargins()
        )
        self.main_apply_voltage_layout.addWidget(self.apply_voltage_label, 0, QtCore.Qt.Alignment.AlignHCenter)
        self.main_apply_voltage_layout.addItem(spacer1)
        self.main_apply_voltage_layout.addLayout(interaction_hbox)
        self.main_apply_voltage_layout.addWidget(self.apply_voltage_button, 0, QtCore.Qt.Alignment.AlignRight)
        self.main_apply_voltage_layout.addItem(spacer1)

        self.help_tab_header = QtWidgets.QLabel("About Apply Voltage")
        self.help_tab_header.setFont(h1_font)

        self.help_tab_desc = QtWidgets.QLabel(lorem.text())
        self.help_tab_desc.setWordWrap(True)

        self.apply_voltage_desc_layout = QtWidgets.QVBoxLayout()
        self.apply_voltage_desc_layout.addWidget(self.help_tab_header)
        # self.apply_voltage_desc_layout.addItem(spacer1)
        self.apply_voltage_desc_layout.addWidget(self.help_tab_desc)
        self.apply_voltage_desc_layout.addItem(spacer1)

        spacer2 = QtWidgets.QSpacerItem(
            20, 0, QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self.apply_voltage_layout = QtWidgets.QHBoxLayout()
        self.apply_voltage_layout.addLayout(self.main_apply_voltage_layout)
        self.apply_voltage_layout.addItem(spacer2)
        self.apply_voltage_layout.addLayout(self.apply_voltage_desc_layout)

    @QtCore.pyqtSlot(float)
    def on_apply_voltage_spin_box_valueChanged(self, value):
        value = round(value, 2)
        self.voltage_to_be_applied = value
        if self.voltage_to_be_applied == self.current_voltage_applied:
            self.apply_voltage_button.setEnabled(False)
        elif not self.apply_voltage_button.isEnabled():
            self.apply_voltage_button.setEnabled(True)
        self.apply_voltage_horizontal_slider.setValue(value * 100 + 500)

    @QtCore.pyqtSlot(int)
    def on_apply_voltage_horizontal_slider_valueChanged(self, value):
        self.voltage_to_be_applied = round(value * 0.01 - 5, 2)
        if self.voltage_to_be_applied == self.current_voltage_applied:
            self.apply_voltage_button.setEnabled(False)
        elif not self.apply_voltage_button.isEnabled():
            self.apply_voltage_button.setEnabled(True)
        self.apply_voltage_spin_box.setValue(self.voltage_to_be_applied)

    @QtCore.pyqtSlot()
    def on_apply_voltage_button_clicked(self):
        # NOTE: self.voltage_to_be_applied must be inverted (since for whatever reason the
        # SEAL kit applies oppositely charged voltage)
        self.current_voltage_applied = self.voltage_to_be_applied
        self.apply_voltage_button.setEnabled(False)
        apply_voltage(self.device_name, self.voltage_offset + offset - self.voltage_to_be_applied)

    def closeEvent(self, close_event):
        self.closing = True
