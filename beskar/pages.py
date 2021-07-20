from .utils import BaseInteractable, TwoDQBarDataItem, apply_voltage, get_file, interact_with_LEDs, LED_position_gen
from PyQt6 import QtCore, QtWidgets, QtCharts, QtGui, QtDataVisualization, QtTest
from .constants import offset, help_tab_fixed_width, help_tab_margins
from fractions import Fraction
from typing import List

import statistics as stats
import darkdetect
import logging
import nidaqmx
import pathlib
import numpy
import random
import time
import csv

logger = logging.getLogger(__name__)


class BasePage(BaseInteractable, QtWidgets.QWidget):
    def super_(self):
        super().__init__()


class ApplyVoltagePage(BasePage):
    def __init__(self, main_window):
        with self.init(main_window):
            self.current_voltage_applied = 0

            self.apply_voltage_label = QtWidgets.QLabel("<h1>Apply Voltage</h1>")

            spacer1 = QtWidgets.QSpacerItem(
                0, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
            )

            self.horizontal_slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            self.horizontal_slider.setMinimumWidth(393)
            self.horizontal_slider.setObjectName('horizontal_slider')
            self.horizontal_slider.setMaximum(5000)
            self.horizontal_slider.setValue(2499)

            self.double_spin_box = QtWidgets.QDoubleSpinBox()
            self.double_spin_box.setObjectName('double_spin_box')
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
            self.interactable_layout.setContentsMargins(10, 10, 0, 0)
            self.interactable_layout.addWidget(self.apply_voltage_label, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
            self.interactable_layout.addItem(spacer1)
            self.interactable_layout.addLayout(interaction_hbox)
            self.interactable_layout.addWidget(self.warning_label, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            self.warning_label.hide()
            self.interactable_layout.addWidget(self.apply_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
            self.interactable_layout.addItem(spacer1)

            with get_file('apply-voltage.md', 'desc', path=True).open() as file:
                # NOTE: Currently if the user compress the window vertically the text
                # will not be fully visualable. Might want to add limitations so that
                # this can't happen.
                self.help_tab = QtWidgets.QLabel(file.read())
                self.help_tab.setFixedWidth(help_tab_fixed_width)
                self.help_tab.setTextFormat(QtCore.Qt.TextFormat.RichText)
                self.help_tab.setWordWrap(True)

            self.desc_layout = QtWidgets.QVBoxLayout()
            self.desc_layout.addWidget(self.help_tab)
            self.desc_layout.addItem(spacer1)
            self.desc_layout.setContentsMargins(help_tab_margins)

            screen_size = QtWidgets.QApplication.primaryScreen().size()
            if Fraction(screen_size.width(), screen_size.height()) >= Fraction(64, 27):
                spacer2_policy = QtWidgets.QSizePolicy.Policy.MinimumExpanding
            else:
                spacer2_policy = QtWidgets.QSizePolicy.Policy.Minimum

            spacer2 = QtWidgets.QSpacerItem(
                20, 0, spacer2_policy, QtWidgets.QSizePolicy.Policy.Minimum
            )

            self.main_layout = QtWidgets.QHBoxLayout()
            self.main_layout.addLayout(self.interactable_layout)
            self.main_layout.addItem(spacer2)
            self.main_layout.addLayout(self.desc_layout)

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

        if self.warning_label.isVisible():
            logger.warning('Abnormally high voltage is about to be applied.')

        if not self.main_window.mocked:
            apply_voltage(
                self.main_window.device_name,
                self.main_window.voltage_offset + offset - self.voltage_to_be_applied
            )

        self.main_window.settings['applied-voltage'] = self.current_voltage_applied

    def set_min_and_max(self):
        self.min_voltage = -round(5 - offset - self.main_window.voltage_offset, 3)
        self.max_voltage = -round(-offset - self.main_window.voltage_offset, 3)

        logger.info(f'self.min_voltage set to {self.min_voltage}.')
        logger.info(f'self.max_voltage set to {self.max_voltage}.')

        self.horizontal_slider.setValue(abs(int(self.min_voltage * 1000)))
        self.double_spin_box.setRange(self.min_voltage, self.max_voltage)

        settings_applied_voltage = self.main_window.settings.get('applied-voltage', 0)
        if (settings_applied_voltage <= self.max_voltage
            and settings_applied_voltage >= self.min_voltage):
            self.double_spin_box.setValue(settings_applied_voltage)


class DarkCurrentPage(BasePage):
    def __init__(self, main_window):
        with self.init(main_window):
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

            with get_file('dark-current.md', 'desc', path=True).open() as file:
                self.help_tab = QtWidgets.QLabel(file.read())
                self.help_tab.setTextFormat(QtCore.Qt.TextFormat.RichText)
                self.help_tab.setFixedWidth(help_tab_fixed_width)
                self.help_tab.setWordWrap(True)

            spacer1 = QtWidgets.QSpacerItem(
                0, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
            )

            self.desc_layout = QtWidgets.QVBoxLayout()
            self.desc_layout.addWidget(self.help_tab)
            self.desc_layout.addItem(spacer1)
            self.desc_layout.setContentsMargins(help_tab_margins)

            spacer2 = spacer2 = QtWidgets.QSpacerItem(
                20, 0, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
            )

            self.main_layout = QtWidgets.QHBoxLayout()
            self.main_layout.addLayout(self.chart_layout)
            self.main_layout.addItem(spacer2)
            self.main_layout.addLayout(self.desc_layout)

    def update_data(self):
        self.scatter.clear()
        if self.main_window.mocked:
            samples = [random.random() * 0.6 for _ in range(10)]
        else:
            with nidaqmx.Task() as task:
                task.ai_channels.add_ai_voltage_chan(
                    f"{self.main_window.device_name}/ai1",
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

        logger.info('Updated dark current readings.')

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


class ScanPage(BasePage):
    def __init__(self, main_window):
        with self.init(main_window):
            self.led_position_gen = LED_position_gen(start_at_zero=True)
            self.led_position = next(self.led_position_gen)

            self.scans = 1

            self.scanning_in_progress = False

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

            self.go_back_button = QtWidgets.QPushButton('Go back to scans')
            self.go_back_button.setObjectName('go_back_button')
            self.go_back_button.hide()

            self.ok_button = QtWidgets.QPushButton('OK')
            self.ok_button.setObjectName('ok_button')

            self.num_of_scan_buttons_layout = QtWidgets.QHBoxLayout()
            self.num_of_scan_buttons_layout.addWidget(
                self.go_back_button,
                stretch=10,
                alignment=QtCore.Qt.AlignmentFlag.AlignRight
            )
            self.num_of_scan_buttons_layout.addWidget(
                self.ok_button,
                alignment=QtCore.Qt.AlignmentFlag.AlignRight
            )

            self.num_of_scan_layout = QtWidgets.QVBoxLayout()
            self.num_of_scan_layout.addItem(spacer1)
            self.num_of_scan_layout.addLayout(self.interaction_layout)
            self.num_of_scan_layout.addLayout(self.num_of_scan_buttons_layout)
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

            self.save_button = QtWidgets.QPushButton('Save scan')
            self.save_button.setObjectName('save_button')
            self.save_button.setEnabled(False)

            self.another_scan_button = QtWidgets.QPushButton('Do another scan(s)')
            self.another_scan_button.setObjectName('another_scan_button')
            self.another_scan_button.setEnabled(False)

            self.buttons_layout = QtWidgets.QHBoxLayout()
            self.buttons_layout.addWidget(self.save_button, stretch=10, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            self.buttons_layout.addWidget(self.another_scan_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            self.bar_chart_layout = QtWidgets.QVBoxLayout()
            self.bar_chart_layout.addWidget(self.bar_charts_tab)
            self.bar_chart_layout.addLayout(self.progress_bar_layout)
            self.bar_chart_layout.addWidget(self.notice_for_reading, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            self.notice_for_reading.hide()
            self.bar_chart_layout.addLayout(self.buttons_layout)
            # self.bar_chart_layout.addWidget(self.another_scan_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            self.bar_chart_layout_widget = QtWidgets.QWidget()
            self.bar_chart_layout_widget.setLayout(self.bar_chart_layout)

            self.stacked_widget = QtWidgets.QStackedWidget()
            self.stacked_widget.addWidget(self.num_of_scan_layout_widget)
            self.stacked_widget.addWidget(self.bar_chart_layout_widget)

            self.main_vbox_layout = QtWidgets.QVBoxLayout()
            self.main_vbox_layout.addWidget(self.scan_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
            self.main_vbox_layout.addWidget(self.stacked_widget)

            with get_file('scan.md', 'desc', path=True).open() as file:
                self.help_tab = QtWidgets.QLabel(file.read())
                self.help_tab.setTextFormat(QtCore.Qt.TextFormat.RichText)
                self.help_tab.setOpenExternalLinks(True)
                self.help_tab.setFixedWidth(help_tab_fixed_width)
                self.help_tab.setWordWrap(True)

            self.desc_layout = QtWidgets.QVBoxLayout()
            self.desc_layout.addWidget(self.help_tab)
            self.desc_layout.addItem(spacer1)
            self.desc_layout.setContentsMargins(help_tab_margins)

            self.spacer2  = QtWidgets.QSpacerItem(
                20, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
            )

            self.main_layout = QtWidgets.QHBoxLayout()
            self.main_layout.addLayout(self.main_vbox_layout)
            self.main_layout.addItem(self.spacer2)
            self.main_layout.addLayout(self.desc_layout)

            self.file_dialog = QtWidgets.QFileDialog(
                self.main_window,
                caption=f'Saving Scan',
                filter='CSV File (*.csv);;Screenshot (*.png)'
            )
            # NOTE: For some reason connectSlotsByName is not working
            # self.file_dialog.setObjectName('file_dialog')
            self.file_dialog.filterSelected.connect(self.on_file_dialog_filterSelected)
            self.file_dialog.accepted.connect(self.on_file_dialog_accepted)
            self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptMode.AcceptSave)

            self.warning_screenshot_dialog = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Icon.Warning,
                'Screenshots may not work properly',
                'Screenshots are still in beta and may not accurately '
                'capture the current view.',
                QtWidgets.QMessageBox.StandardButton.Ok,
                self.main_window
            )

        self.spin_box.setValue(self.main_window.settings.get('scans', 1))

    def create_bar_graph(self):
        graph_components = [
            QtDataVisualization.Q3DBars(),
            QtDataVisualization.QBar3DSeries(),
            numpy.zeros((8, 8)).view(TwoDQBarDataItem)
        ]
        graph_components[0].addSeries(graph_components[1])
        graph_components[0].rowAxis().setRange(0, 7)
        graph_components[0].columnAxis().setRange(0, 7)
        graph_components.append(QtWidgets.QWidget.createWindowContainer(graph_components[0]))

        self.bar_charts.append(graph_components)

        self.bar_charts_tab.addTab(self.bar_charts[len(self.bar_charts) - 1][3], f'Scan {len(self.bar_charts)}')

    @QtCore.pyqtSlot(int)
    def on_bar_charts_tab_currentChanged(self, tab):
        if tab + 1 == len(self.bar_charts):
            self.progress_bar.show()
            self.scanning_progress_label.show()
            self.save_button.setEnabled(not self.scanning_in_progress)
        else:
            self.progress_bar.hide()
            self.scanning_progress_label.hide()
            self.notice_for_reading.hide()
            self.save_button.setEnabled(True)

    @QtCore.pyqtSlot(int)
    def on_spin_box_valueChanged(self, value):
        self.scans = value
        if value == 1:
            self.spin_box.setSuffix(' Scan')
        else:
            self.spin_box.setSuffix(' Scans')

    @QtCore.pyqtSlot()
    def on_ok_button_clicked(self):
        self.scanning_in_progress = True

        self.main_layout.removeItem(self.spacer2)

        self.another_scan_button.setEnabled(False)

        self.stacked_widget.setCurrentIndex(1)

        self.main_window.settings['scans'] = self.scans

        scan_offset = len(self.bar_charts_tab)

        logger.info(f'{self.scans} have been initiated.')

        for scan_number in range(self.scans):
            scan_number += scan_offset

            self.create_bar_graph()
            self.bar_charts_tab.setCurrentIndex(scan_number)

            self.progress_bar.setValue(0)

            self.main_window.dark_current_widget.update_data()
            dark_current = stats.mean(self.main_window.dark_current_widget.samples)

            length = 64 if len(self.led_position) == 3 else 65
            self.progress_bar.setMaximum(length)

            if not self.main_window.mocked:
                interact_with_LEDs(self.main_window.device_name, 'on&off')

            # Delay for signal to flash LEDs
            QtTest.QTest.qWait(412)

            for progress in range(length):
                if self.main_window.exiting:
                    return
                loop_start = time.time()
                if self.main_window.mocked:
                    samples = [random.random() for _ in range(10)]
                else:
                    with nidaqmx.Task() as task:
                        task.ai_channels.add_ai_voltage_chan(
                            f'{self.main_window.device_name}/ai1', min_val=-10, max_val=10
                        )
                        samples = task.read(10)
                self.bar_charts[scan_number][2][
                    self.led_position[0], self.led_position[1]
                ] = max(samples) - dark_current
                self.bar_charts[scan_number][1].dataProxy().resetArray(
                    self.bar_charts[scan_number][2].tolist(convert_to_bar_data=True)
                )

                self.progress_bar.setValue(progress + 1)

                self.led_position = next(self.led_position_gen)

                if self.bar_charts_tab.currentIndex() == scan_number:
                    if self.bar_charts[scan_number][2].last_values_zero():
                        logger.info('The last four values read from the SEAL kit have been zeros.')
                        self.notice_for_reading.show()
                    else:
                        self.notice_for_reading.hide()

                computation_time = time.time() - loop_start

                if progress == 0:
                    # Delay between the first and second LED flash
                    QtTest.QTest.qWait(492 - computation_time * 1000)
                elif progress == 1:
                    # Delay between second and thrid LED flash
                    QtTest.QTest.qWait(820 - 1 - computation_time * 1000)
                elif progress == length - 1 and scan_number != self.scans + scan_offset - 1:
                    QtTest.QTest.qWait(1000)
                else:
                    # Delay between all other LED flashes
                    QtTest.QTest.qWait(860 - 1 - computation_time * 1000)

        self.scanning_in_progress = False

        self.notice_for_reading.hide()

        if self.go_back_button.isHidden():
            self.go_back_button.show()

        self.save_button.setEnabled(True)
        self.another_scan_button.setEnabled(True)

    @QtCore.pyqtSlot()
    def on_save_button_clicked(self):
        self.file_dialog.setLabelText(
            QtWidgets.QFileDialog.DialogLabel.Accept,
            f'Save Scan {self.bar_charts_tab.currentIndex() + 1}'
        )

        # NOTE: If the OS is in dark mode, when a file dialog
        # is displayed it will be all black. For some reason
        # using the .setWindowIcon method does not change the
        # icon.  The only way to change the file dialog icon
        # is to change the main application icon. So in order
        # for the icon to visible against a black background we
        # must use the beskar-icon-white.png icon. The code below
        # will temporarily set the main application icon to the white
        # icon, while the file dialog is being created so that the
        # file dialog inherits this icon as its icon. Once the file
        # dialog is created the original icon is set to the main window.

        if darkdetect.isDark():
            if not self.main_window.white_icon:
                white_icon_path = get_file('beskar-icon-white.png')
                if white_icon_path:
                    self.main_window.white_icon = QtGui.QIcon(white_icon_path)

            if self.main_window.white_icon:
                self.main_window.setWindowIcon(self.main_window.white_icon)

        self.file_dialog.open()

        if darkdetect.isDark():
            QtTest.QTest.qWait(800)
            if self.main_window.icon:
                self.main_window.setWindowIcon(self.main_window.icon)

    @QtCore.pyqtSlot(str)
    def on_file_dialog_filterSelected(self, file_filter: str):
        if '.png' in file_filter:
            self.warning_screenshot_dialog.open()

    @QtCore.pyqtSlot()
    def on_file_dialog_accepted(self):
        # NOTE: The file dialog automatically handles
        # attempting to write to folders that require
        # elevate privileges to write to.

        file_ext = self.file_dialog.selectedNameFilter()
        selected = pathlib.Path(self.file_dialog.selectedFiles()[0])
        current_tab = self.bar_charts_tab.currentIndex()
        if '.csv' in file_ext:
            with selected.open(mode='w', newline='') as file:
                writer = csv.writer(file, csv.excel)
                writer.writerow([f'Column {num + 1}' for num in range(8)])
                writer.writerows(self.bar_charts[current_tab][2])
        elif '.png' in file_ext:
            # TODO: Fix inconsistent and/or bad screenshots
            q3dbar = self.bar_charts[current_tab][0]
            q3dbar.renderToImage().save(str(selected))
        else:
            raise RuntimeError(f'This should never be triggered: {file_ext=}')

        logger.info(f'{selected} has been created in order to save Scan {current_tab}.')

    @QtCore.pyqtSlot()
    def on_another_scan_button_clicked(self):
        self.main_layout.insertItem(1, self.spacer2)
        self.stacked_widget.setCurrentIndex(0)

    @QtCore.pyqtSlot()
    def on_go_back_button_clicked(self):
        self.main_layout.removeItem(self.spacer2)
        self.stacked_widget.setCurrentIndex(1)
