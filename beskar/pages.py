from PyQt6 import QtCore, QtWidgets, QtCharts, QtGui
from .utils import apply_voltage
from .constants import offset

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
        # NOTE: Need to use .connect since for some reason
        # since connectBySlots does not detect the slot
        self.scatter.hovered.connect(self.on_scatter_hovered)

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

        self.update_data()

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
            self.y_axis.setRange(min(self.samples) * 0.9, max(self.samples) * 1.1)
            for num, sample in enumerate(self.samples):
                self.scatter.append(num + 1, sample)

    @QtCore.pyqtSlot()
    def on_refresh_button_clicked(self):
        self.update_data()

    def on_scatter_hovered(self, point: QtCore.QPointF, state):
        # TODO: Might want to add the ability to copy the values

        # NOTE: This is a bit buggy at the moment and does not display for 10 seconds.
        # Also only shows when the mouse is stationary.

        QtWidgets.QToolTip.showText(
            QtGui.QCursor.pos(), str((int(point.x()), point.y())), msecShowTime=10_000
        )
