from .utils import apply_voltage, interact_with_LEDs, LED_position_gen, TwoDQBarDataItem
from PyQt6 import QtCore, QtWidgets, QtCharts, QtGui, QtDataVisualization, QtTest
from .constants import offset
from typing import List

import statistics as stats
import nidaqmx
import numpy
import time
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


class ScanPage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self.parent = parent

        self.led_position = LED_position_gen(start_at_zero=True)

        self.scans = 1

        self.scan_label = QtWidgets.QLabel('<h1>Scan</h1>')

        spacer1 = QtWidgets.QSpacerItem(
            0, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self.select_label = QtWidgets.QLabel(
            'Select the number of scans you would like to do:'
        )

        self.spin_box = QtWidgets.QSpinBox()
        self.spin_box.setObjectName('spin_box')
        self.spin_box.setRange(1, 10)
        self.spin_box.setSuffix(' Scan')

        self.interaction_layout = QtWidgets.QHBoxLayout()
        self.interaction_layout.addWidget(
            self.select_label, stretch=10, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.interaction_layout.addWidget(
            self.spin_box, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )

        self.ok_button = QtWidgets.QPushButton('OK')
        self.ok_button.setObjectName('ok_button')

        self.num_of_scan_layout = QtWidgets.QVBoxLayout()
        self.num_of_scan_layout.addItem(spacer1)
        self.num_of_scan_layout.addLayout(self.interaction_layout)
        self.num_of_scan_layout.addWidget(
            self.ok_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight
        )
        self.num_of_scan_layout.addItem(spacer1)

        self.num_of_scan_layout_widget = QtWidgets.QWidget()
        self.num_of_scan_layout_widget.setLayout(self.num_of_scan_layout)

        self.bar_charts: List[
            List[
                QtDataVisualization.Q3DBars,
                QtDataVisualization.QBar3DSeries,
                TwoDQBarDataItem,
                QtWidgets.QWidget
            ]
        ] = list()


        self.bar_charts_tab = QtWidgets.QTabWidget()
        self.bar_charts_tab.setObjectName('bar_charts_tab')

        self.scanning_progress_label = QtWidgets.QLabel('Scanning progress:')
        self.progress_bar = QtWidgets.QProgressBar()

        self.progress_bar_layout = QtWidgets.QHBoxLayout()
        self.progress_bar_layout.addWidget(self.scanning_progress_label)
        self.progress_bar_layout.addWidget(self.progress_bar)

        self.notice_for_reading = QtWidgets.QLabel(
            'Even though it looks like nothing is happening, <b>data is still being read!</b> '
            "The reason you can't see anything happening on screen is because the values being "
            'read are zeros.'
        )
        self.notice_for_reading.setSizePolicy(
            self.notice_for_reading.sizePolicy().horizontalPolicy(), QtWidgets.QSizePolicy.Policy.Fixed
        )

        self.another_scan_button = QtWidgets.QPushButton('Do another scan')
        self.another_scan_button.setObjectName('another_scan_button')
        self.another_scan_button.setEnabled(False)

        self.bar_chart_layout = QtWidgets.QVBoxLayout()
        self.bar_chart_layout.addWidget(self.bar_charts_tab)
        self.bar_chart_layout.addLayout(self.progress_bar_layout)
        self.bar_chart_layout.addWidget(self.notice_for_reading, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
        self.notice_for_reading.hide()
        self.bar_chart_layout.addWidget(self.another_scan_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)



        self.bar_chart_layout_widget = QtWidgets.QWidget()
        self.bar_chart_layout_widget.setLayout(self.bar_chart_layout)

        self.stacked_widget = QtWidgets.QStackedWidget()
        self.stacked_widget.addWidget(self.num_of_scan_layout_widget)
        self.stacked_widget.addWidget(self.bar_chart_layout_widget)

        self.main_vbox_layout = QtWidgets.QVBoxLayout()
        self.main_vbox_layout.addWidget(self.scan_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.main_vbox_layout.addWidget(self.stacked_widget)

        self.help_tab_header = QtWidgets.QLabel('<h1>About Scanning</h1>')

        self.help_tab_desc = QtWidgets.QLabel(lorem.text())
        self.help_tab_desc.setWordWrap(True)

        self.desc_layout = QtWidgets.QVBoxLayout()
        self.desc_layout.addWidget(self.help_tab_header)
        self.desc_layout.addWidget(self.help_tab_desc)
        self.desc_layout.addItem(spacer1)

        self.spacer2  = QtWidgets.QSpacerItem(
            20, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
        )

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(self.main_vbox_layout)
        self.layout.addItem(self.spacer2)
        self.layout.addLayout(self.desc_layout)

        self.setLayout(self.layout)

        QtCore.QMetaObject.connectSlotsByName(self)

    def create_bar_graph(self):
        graph_components = [QtDataVisualization.Q3DBars(), QtDataVisualization.QBar3DSeries(), numpy.zeros((8, 8)).view(TwoDQBarDataItem)]
        graph_components[0].addSeries(graph_components[1])
        graph_components[0].rowAxis().setRange(0, 7)
        graph_components[0].columnAxis().setRange(0, 7)
        graph_components.append(QtWidgets.QWidget.createWindowContainer(graph_components[0]))

        self.bar_charts.append(graph_components)

        self.bar_charts_tab.addTab(self.bar_charts[len(self.bar_charts) - 1][3], f'Scan {len(self.bar_charts)}')

    @QtCore.pyqtSlot(int)
    def on_bar_charts_tab_tabBarClicked(self, tab):
        if tab + 1 == len(self.bar_charts):
            self.progress_bar.show()
            self.scanning_progress_label.show()
        else:
            self.progress_bar.hide()
            self.scanning_progress_label.hide()
            self.notice_for_reading.hide()

    @QtCore.pyqtSlot(int)
    def on_spin_box_valueChanged(self, value):
        self.scans = value
        if value == 1:
            self.spin_box.setSuffix(' Scan')
        else:
            self.spin_box.setSuffix(' Scans')

    @QtCore.pyqtSlot()
    def on_ok_button_clicked(self):
        self.layout.removeItem(self.spacer2)

        self.another_scan_button.setEnabled(False)

        self.stacked_widget.setCurrentIndex(1)

        differences = []

        scan_offset = len(self.bar_charts_tab)

        interact_with_LEDs(self.parent.device_name, 'on')

        # NOTE: print statements are and will be important in
        # solving issue #2

        for scan_number in range(self.scans):
            scan_number += scan_offset

            self.create_bar_graph()
            self.bar_charts_tab.setCurrentIndex(scan_number)

            self.progress_bar.setValue(0)

            self.parent.dark_current_widget.update_data()
            dark_current = stats.mean(self.parent.dark_current_widget.samples)

            led_position = next(self.led_position)
            length = 64 if led_position == (1, 3) else 65
            # print(f"length={length}")
            self.progress_bar.setMaximum(length)

            # Delay for signal to flash LEDs
            start = time.time()
            QtTest.QTest.qWait(533)
            # print(f'First time: {time.time() - start} (should be close to 533)')

            for progress in range(length):
                loop_start = time.time()
                with nidaqmx.Task() as task:
                    task.ai_channels.add_ai_voltage_chan(
                        f'{self.parent.device_name}/ai1', min_val=-10, max_val=10
                    )
                    samples = task.read(10)
                    self.bar_charts[scan_number][2][led_position[0], led_position[1]] = max(samples) - dark_current
                    self.bar_charts[scan_number][1].dataProxy().resetArray(
                        self.bar_charts[scan_number][2].tolist(convert_to_bar_data=True)
                    )

                self.progress_bar.setValue(progress + 1)

                led_position = next(self.led_position)

                if self.bar_charts_tab.currentIndex() == scan_number:
                    if self.bar_charts[scan_number][2].last_values_zero():
                        self.notice_for_reading.show()
                    else:
                        self.notice_for_reading.hide()

                computation_time = time.time() - loop_start
                # print(f'writing to graph took: {computation_time}')

                if progress == 0:
                    expected_loop_time = 483
                    # Delay between the first and second LED flash
                    # start = time.time()
                    QtTest.QTest.qWait(483 - computation_time * 1000)
                    # print(f"Time: {time.time() - start}, should be close to 483")
                elif progress == 1:
                    expected_loop_time = 800
                    # Delay between second and thrid LED flash
                    start = time.time()
                    QtTest.QTest.qWait(800 - 1 - computation_time * 1000)
                    # print(f"Time: {time.time() - start} should be close to 800")
                elif progress == 2:
                    expected_loop_time = 850
                    # Delay between third and fourth LED flash
                    # start = time.time()
                    QtTest.QTest.qWait(850 - 1 - computation_time * 1000)
                    # print(f"Time: {time.time() - start} should be close to 850")
                else:
                    expected_loop_time = 867
                    # Delay between all other LED flashes
                    start = time.time()
                    QtTest.QTest.qWait(867 - 1 - computation_time * 1000)
                    # print(f"Time: {time.time() - start} should be close to 867")
                actual_loop_time = (time.time() - loop_start) * 1000
                differences.append(actual_loop_time - expected_loop_time)
                # print(f'\n\n**loop time: {actual_loop_time} (should take {expected_loop_time})**\n\n')

        interact_with_LEDs(self.parent.device_name, 'off')

        self.notice_for_reading.hide()
        # print(f'was off by {sum(differences)}')
        # print(f'len(tab)={len(self.bar_charts_tab)}')

        self.another_scan_button.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_another_scan_button_clicked(self):
        self.layout.insertItem(1, self.spacer2)
        self.stacked_widget.setCurrentIndex(0)
