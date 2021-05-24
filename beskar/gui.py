from .popups import MultipleSEALKitsPopup, NoSEALKitPopup, EnterVoltsPopup
from PyQt6 import QtCore, QtCharts, QtWidgets, QtGui
from nidaqmx.system import System
from .constants import offset
from .utils import apply_voltage

import nidaqmx
import lorem


class ApplyVoltagePage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.current_voltage_applied = 0

        self.apply_voltage_label = QtWidgets.QLabel("<h1>Apply Voltage</h1>")

        spacer1 = QtWidgets.QSpacerItem(
            0, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.min_voltage = -round(5 - offset - self.parent.voltage_offset, 3)
        self.max_voltage = -round(-offset - self.parent.voltage_offset, 3)

        self.horizontal_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
        self.horizontal_slider.setObjectName('horizontal_slider')
        self.horizontal_slider.setMaximum(5000)
        self.horizontal_slider.setValue(abs(int(self.min_voltage * 1000)))

        self.double_spin_box = QtWidgets.QDoubleSpinBox()
        self.double_spin_box.setObjectName('double_spin_box')
        self.double_spin_box.setRange(self.min_voltage, self.max_voltage)
        self.double_spin_box.setSingleStep(0.001)
        self.double_spin_box.setDecimals(3)
        self.double_spin_box.setSuffix(' Volts')

        self.warning_label = QtWidgets.QLabel(
            '<b>WARNING:</b> This voltage may not be applied accurately'
            ' due to limitations with the SEAL Kit.'
        )

        self.apply_button = QtWidgets.QPushButton('Apply')
        self.apply_button.setObjectName('apply_button')
        self.apply_button.setEnabled(False)

        interaction_hbox = QtWidgets.QHBoxLayout()
        interaction_hbox.addWidget(self.horizontal_slider)
        interaction_hbox.addWidget(self.double_spin_box)

        self.interactable_layout = QtWidgets.QVBoxLayout()
        self.interactable_layout.contentsMargins().setLeft(1000)
        self.interactable_layout.contentsMargins().setRight(1000)
        self.interactable_layout.setContentsMargins(
            self.interactable_layout.contentsMargins()
        )
        self.interactable_layout.addWidget(self.apply_voltage_label, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.interactable_layout.addItem(spacer1)
        self.interactable_layout.addLayout(interaction_hbox)
        self.interactable_layout.addWidget(self.warning_label, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.warning_label.hide()
        self.interactable_layout.addWidget(self.apply_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        self.interactable_layout.addItem(spacer1)

        self.help_tab_header = QtWidgets.QLabel("<h1>About Apply Voltage</h1>")

        self.help_tab_desc = QtWidgets.QLabel(lorem.text())
        self.help_tab_desc.setWordWrap(True)

        self.desc_layout = QtWidgets.QVBoxLayout()
        self.desc_layout.addWidget(self.help_tab_header)
        # self.desc_layout.addItem(spacer1)
        self.desc_layout.addWidget(self.help_tab_desc)
        self.desc_layout.addItem(spacer1)

        spacer2 = QtWidgets.QSpacerItem(
            20, 0, QtWidgets.QSizePolicy.Policy.MinimumExpanding, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.interactable_layout)
        self.layout.addItem(spacer2)
        self.layout.addLayout(self.desc_layout)

        self.setLayout(self.layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    @QtCore.pyqtSlot(float)
    def on_double_spin_box_valueChanged(self, value):
        value = round(value, 3)
        self.voltage_to_be_applied = value
        if value >= 0.75 * self.max_voltage or value <= 0.75 * self.min_voltage:
            self.warning_label.show()
        else:
            self.warning_label.hide()
        if self.voltage_to_be_applied == self.current_voltage_applied:
            self.apply_button.setEnabled(False)
        elif not self.apply_button.isEnabled():
            self.apply_button.setEnabled(True)
        self.horizontal_slider.setValue(round((value - self.min_voltage) * 1000))

    @QtCore.pyqtSlot(int)
    def on_horizontal_slider_valueChanged(self, value):
        self.voltage_to_be_applied = round(value * 0.001 + self.min_voltage, 3)
        if self.voltage_to_be_applied == self.current_voltage_applied:
            self.apply_button.setEnabled(False)
        elif not self.apply_button.isEnabled():
            self.apply_button.setEnabled(True)
        self.double_spin_box.setValue(self.voltage_to_be_applied)

    @QtCore.pyqtSlot()
    def on_apply_button_clicked(self):
        # NOTE: self.voltage_to_be_applied must be inverted (since for whatever reason the
        # SEAL kit applies oppositely charged voltage)
        # See this for reference: https://github.com/Ahsoka/beskar/blob/main/legacy/get_led_data_12.m#L324
        # This is the implementation in the legacy software
        self.current_voltage_applied = self.voltage_to_be_applied
        self.apply_button.setEnabled(False)
        apply_voltage(self.parent.device_name, self.parent.voltage_offset + offset - self.voltage_to_be_applied)


class DarkCurrentPage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.x_axis = QtCharts.QCategoryAxis()
        self.x_axis.setRange(0.5, 10.5)
        for num in range(10):
            self.x_axis.append(str(num + 1), num + 1)
        self.x_axis.setLabelsPosition(QtCharts.QCategoryAxis.AxisLabelsPosition.AxisLabelsPositionOnValue)
        self.x_axis.setTitleText('Sample Number')

        self.y_axis = QtCharts.QValueAxis()
        self.y_axis.setTitleText('Voltage')

        self.scatter = QtCharts.QScatterSeries()

        self.chart = QtCharts.QChart()
        self.chart.addSeries(self.scatter)
        self.chart.addAxis(self.x_axis, QtCore.Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.y_axis, QtCore.Qt.AlignmentFlag.AlignLeft)
        self.scatter.attachAxis(self.x_axis)
        self.scatter.attachAxis(self.y_axis)
        self.chart.setAnimationOptions(QtCharts.QChart.AnimationOption.SeriesAnimations)
        self.chart.setTitle('<h1>Dark Current</h1>')
        self.chart.legend().hide()

        self.chart_view = QtCharts.QChartView(self.chart)
        self.chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        self.refresh_button = QtWidgets.QPushButton('Refresh')
        self.refresh_button.setObjectName('refresh_button')

        self.chart_layout = QtWidgets.QVBoxLayout()
        self.chart_layout.addWidget(self.chart_view)
        self.chart_layout.addWidget(self.refresh_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        self.help_tab_header = QtWidgets.QLabel("<h1>About Dark Current</h1>")

        self.help_tab_desc = QtWidgets.QLabel(lorem.text())
        self.help_tab_desc.setWordWrap(True)

        spacer1 = QtWidgets.QSpacerItem(
            0, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.desc_layout = QtWidgets.QVBoxLayout()
        self.desc_layout.addWidget(self.help_tab_header)
        self.desc_layout.addWidget(self.help_tab_desc)
        self.desc_layout.addItem(spacer1)

        spacer2 = spacer2 = QtWidgets.QSpacerItem(
            20, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.chart_layout)
        self.layout.addItem(spacer2)
        self.layout.addLayout(self.desc_layout)

        self.setLayout(self.layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    def update_data(self):
        self.scatter.clear()
        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan(
                f"{self.parent.device_name}/ai1",
                min_val=-10,
                max_val=10
            )
            samples = task.read(number_of_samples_per_channel=10)
            if not hasattr(self, 'samples'):
                self.samples = samples
            elif samples == self.samples:
                self.chart.removeSeries(self.scatter)
                self.chart.addSeries(self.scatter)
                self.scatter.attachAxis(self.x_axis)
                self.scatter.attachAxis(self.y_axis)
            self.samples = samples
            self.y_axis.setRange(min(self.samples) * 0.9 ,max(self.samples) * 1.1)
            for num, sample in enumerate(self.samples):
                self.scatter.append(num + 1, sample)

    @QtCore.pyqtSlot()
    def on_refresh_button_clicked(self):
        self.update_data()

class BeskarWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

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
            self.enter_volts_popup.exec()

        self.create_options_menu()

        self.apply_voltage_widget = ApplyVoltagePage(self)

        self.dark_current_widget = DarkCurrentPage(self)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.stacked_widget.addWidget(self.apply_voltage_widget)
        self.stacked_widget.addWidget(self.dark_current_widget)

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

    @QtCore.pyqtSlot()
    def on_scan_menu_button_clicked(self):
        self.scan_menu.setChecked(True)
        self.apply_voltage_menu.setChecked(False)
        self.dark_current_menu.setChecked(False)

        # TODO: Implement scan page
