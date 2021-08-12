from PyQt6 import QtCore, QtWidgets, QtCharts, QtGui, QtDataVisualization, QtTest
from .widgets import DoubleSpinBox, LabelWithIcon, LinkHoverColorChange
from .constants import offset, help_tab_fixed_width, help_tab_margins
from typing import Union, Tuple, List
from nidaqmx.system import System
from . import settings
from .utils import (
    get_number_of_devices,
    interact_with_LEDs,
    BaseInteractable,
    TwoDQBarDataItem,
    LED_position_gen,
    apply_voltage,
    sort_frames,
    get_folder,
    get_file
)

import statistics as stats
import darkdetect
import itertools
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


class NoSEALKitPage(BasePage):
    def __init__(
        self,
        main_window,
        have_drivers: bool,
        refresh_icon_dir_str: str = 'images/refresh-icon-frames'
    ):
        with self.init(main_window):
            self.have_drivers = have_drivers
            self.animation_in_progress = False

            refresh_icon_dir = get_folder(refresh_icon_dir_str)
            self.refresh_animated = bool(refresh_icon_dir)
            if self.refresh_animated:
                self.frames = sort_frames(refresh_icon_dir, '*.svg')
                first_refresh_icon_frame = next(self.frames)

            self.header = QtWidgets.QLabel('No SEAL Kit Detected')
            self.header.setObjectName('no_SEAL_kit_header')
            font = self.header.font()
            font.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
            self.header.setFont(font)
            self.header.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed
            )

            if warning_icon_loc := get_file('warning-icon.svg'):
                self.desc = LabelWithIcon(
                    warning_icon_loc,
                    link_color1='#0078D8',
                    link_color2='#777777'
                )
            else:
                self.desc = LinkHoverColorChange('#0078D8', '#777777')
            self.desc.setWordWrap(True)
            self.desc.setObjectName('no_SEAL_kit_desc')
            self.desc.setFixedWidth(300)
            if self.have_drivers:
                self.desc.setText(
                    'Double check the SEAL kit is plugged in.'
                )
                self.desc.setMinimumHeight(48)
            else:
                self.desc.setText(
                    '<b>WARNING:</b> Drivers are not detected on this computer. '
                    'In order to connect with the SEAL kit you must install the drivers from '
                    '<a style="color: {}; text-decoration: none" href="https://www.ni.com/en-us/support/downloads/drivers/download.ni-daqmx.html#348669">here</a>.'
                )
                self.desc.setOpenExternalLinks(True)
                self.desc.setMinimumHeight(100)
            self.desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
            self.desc.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )

            self.refresh_button = QtWidgets.QPushButton('Refresh')
            self.refresh_button.setObjectName('no_SEAL_refresh_button')
            if refresh_icon_loc := get_file('refresh-icon.svg'):
                self.refresh_button.setIcon(QtGui.QIcon(refresh_icon_loc))
            elif self.refresh_animated:
                self.refresh_button.setIcon(QtGui.QIcon(str(first_refresh_icon_frame)))
            self.refresh_button.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
            self.refresh_button.setFixedWidth(300)
            self.refresh_button.clicked.connect(self.mouse_press_event)

            self.no_SEAL_kit_button = QtWidgets.QPushButton("Don't have a SEAL kit")
            self.no_SEAL_kit_button.setObjectName('no_SEAL_kit_button')
            self.no_SEAL_kit_button.setFixedWidth(300)
            if disconnected_icon_loc := get_file('SEAL-kit-disconnected-icon.svg'):
                self.no_SEAL_kit_button.setIcon(QtGui.QIcon(disconnected_icon_loc))
            self.no_SEAL_kit_button.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)

            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.setSpacing(0)
            self.main_layout.addWidget(
                self.header,
                alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter
            )
            self.main_layout.addSpacing(10)
            self.main_layout.addWidget(
                self.desc,
                alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter
            )
            self.main_layout.addSpacing(50)
            self.main_layout.addWidget(self.refresh_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addSpacing(20)
            self.main_layout.addWidget(self.no_SEAL_kit_button, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addStretch(10)

    @QtCore.pyqtSlot()
    def on_no_SEAL_refresh_button_clicked(self):
        if not self.animation_in_progress:
            self.refresh_button.setText('Looking')

            if self.refresh_animated:
                self.animation_in_progress = True
                for frame_num, frame in zip(range(28), self.frames):
                    QtTest.QTest.qWait(36)
                    self.refresh_button.setIcon(QtGui.QIcon(str(frame)))
                    if frame_num != 0 and frame_num % 5 == 0:
                        self.refresh_button.setText(f'{self.refresh_button.text()}.')
            else:
                for _ in range(5):
                    QtTest.QTest.qWait(200)
                    self.refresh_button.setText(f'{self.refresh_button.text()}.')
            if self.have_drivers:
                num_of_devices = get_number_of_devices(system=False)
                if num_of_devices == 0:
                    self.desc.setText(
                        '<p style="text-indent: 20px">SEAL kit not detected, '
                        'try refreshing again.</p>'
                    )
                elif self.main_window.stacked_widget.currentIndex() == 0:
                    self.main_window.next_page('select')
            self.animation_in_progress = False
            self.refresh_button.setText('Refresh')

    @QtCore.pyqtSlot()
    def on_no_SEAL_kit_button_clicked(self):
        self.main_window.next_page('mocked')

    def mouse_press_event(self) -> None:
        if ((self.refresh_button.hasFocus() and not self.refresh_button.underMouse())
            or (self.no_SEAL_kit_button.hasFocus() and not self.no_SEAL_kit_button.underMouse())):
            self.main_window.set_focus()


class SelectSEALKitPage(BasePage):
    def __init__(self, main_window):
        with self.init(main_window):
            self.header = QtWidgets.QLabel('Select SEAL Kit')
            self.header.setObjectName('select_SEAL_kit_header')

            self.buttons_group = QtWidgets.QButtonGroup()
            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.setSpacing(0)
            self.main_layout.addWidget(
                self.header, alignment=QtCore.Qt.AlignmentFlag.AlignCenter
            )
            self.main_layout.addSpacing(30)
            device_names = System.local().devices.device_names
            # device_names = [f"Dev {num + 1}" for num in range(4)]
            for index, device_name in enumerate(device_names):
                radio_button = QtWidgets.QRadioButton(f" {device_name}")
                radio_button.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
                radio_button.setObjectName(f'select_SEAL_kit_radio_button{index}')
                radio_button.clicked.connect(self.mouse_press_event)
                radio_button.setFixedWidth(205)
                if index == 0:
                    radio_button.setChecked(True)

                self.buttons_group.addButton(radio_button, id=index)
                self.main_layout.addWidget(
                    radio_button,
                    alignment=QtCore.Qt.AlignmentFlag.AlignCenter
                )
                if index != len(device_names) - 1:
                    self.main_layout.addSpacing(20)
            self.main_layout.addStretch(10)

            self.current_button = itertools.cycle(range(len(device_names)))

        self.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)

    def focusInEvent(self, focus_event: QtGui.QFocusEvent) -> None:
        self.buttons_group.button(0).setFocus(QtCore.Qt.FocusReason.TabFocusReason)

    def focusNextPrevChild(self, next_: bool) -> bool:
        buttons = self.buttons_group.buttons()
        try:
            button_index = buttons.index(self.focusWidget())
        except ValueError:
            return False
        if next_:
            if button_index == len(buttons) - 1:
                return False
            new_index = button_index + 1
        else:
            if button_index == 0:
                return False
            new_index = button_index - 1

        self.buttons_group.button(new_index).setFocus(
            QtCore.Qt.FocusReason.TabFocusReason
        )
        return True

    def mouse_press_event(self) -> None:
        for button in self.buttons_group.buttons():
            if button.hasFocus() and not button.underMouse():
                self.main_window.set_focus()


class MockedModePage(BasePage):
    def __init__(self, main_window):
        with self.init(main_window):
            desc_width = 270

            self.header = QtWidgets.QLabel('Mocked Mode')
            self.header.setObjectName('mocked_mode_header')
            self.header.setFixedWidth(desc_width)
            self.header.setFixedHeight(30)
            self.header.setSizePolicy(
                QtWidgets.QSizePolicy.Policy.Minimum,
                QtWidgets.QSizePolicy.Policy.Fixed
            )

            self.desc = QtWidgets.QLabel(
                get_file('mocked-mode.md', 'desc', path=True).read_text()
                # NOTE: This will error out if the file doesn't exist but maybe
                # that is a good thing?
            )
            self.desc.setObjectName('mocked_mode_desc')
            self.desc.setWordWrap(True)
            self.desc.setFixedWidth(desc_width)
            self.desc.setMinimumHeight(220)
            self.desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)


            self.main_layout = QtWidgets.QVBoxLayout()
            self.main_layout.setSpacing(0)
            self.main_layout.addWidget(
                self.header,
                alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
            )
            self.main_layout.addSpacing(10)
            self.main_layout.addWidget(
                self.desc,
                alignment=QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignHCenter
            )
            self.main_layout.addStretch(10)


class BaseSetVoltagePage(BasePage):
    def __init__(
        self,
        header: str,
        about_header: str,
        desc: str,
        desc_width,
        spin_box_range: Tuple[Union[int, int], Union[float, float]],
        suffix: str = ' Volts'
    ):
        self.set_with_settings = False

        self.header = QtWidgets.QLabel(header)
        self.header.setObjectName(f"{'_'.join(header.lower())}_header")

        # TODO: Make slider like an Apple slider where you can click on a given
        # location and slider will automatically move to that location.
        # Reference: https://stackoverflow.com/questions/52689047/moving-qslider-to-mouse-click-position
        self.slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Vertical)
        self.slider.setMinimumWidth(30)
        self.slider.setObjectName('slider')

        self.double_spin_box = DoubleSpinBox()
        self.double_spin_box.setRange(spin_box_range[0], spin_box_range[1])
        self.double_spin_box.setSingleStep(0.001)
        self.double_spin_box.setDecimals(3)
        self.double_spin_box.setObjectName('spin_box')
        self.double_spin_box.setSuffix(suffix)

        self.slider_layout = QtWidgets.QVBoxLayout()
        self.slider_layout.addWidget(
            self.slider,
            alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
        )
        self.slider_layout.addSpacing(8)
        self.slider_layout.addWidget(
            self.double_spin_box,
            alignment=QtCore.Qt.AlignmentFlag.AlignHCenter
        )

        self.about_header = QtWidgets.QLabel(about_header)
        self.about_header.setObjectName(f"{'_'.join(about_header.split())}_subheader")

        self.desc = QtWidgets.QLabel(desc)
        self.desc.setFixedWidth(desc_width)
        self.desc.setWordWrap(True)

        self.about_layout = QtWidgets.QVBoxLayout()
        self.about_layout.addWidget(self.about_header)
        self.about_layout.addWidget(self.desc)
        self.about_layout.addStretch(10)

        self.middle_layout = QtWidgets.QHBoxLayout()
        self.middle_layout.addLayout(self.slider_layout)
        self.middle_layout.addStretch(20)
        self.middle_layout.addLayout(self.about_layout)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.addWidget(self.header)
        self.main_layout.addSpacing(30)
        self.main_layout.addLayout(self.middle_layout)


class VoltageOffsetPage(BaseSetVoltagePage):
    def __init__(self, main_window):
        with self.init(main_window):
            super().__init__(
                'Select Voltage Offset',
                'About Voltage Offset',
                get_file('voltage-offset.md', 'desc', path=True).read_text(),
                280,
                (0, 1)
            )
            self.main_layout.addSpacing(32)

            self.slider.setMaximum(1000)

    @QtCore.pyqtSlot(int)
    def on_slider_valueChanged(self, position):
        voltage = position / 1000
        self.double_spin_box.setValue(voltage)

    @QtCore.pyqtSlot(float)
    def on_spin_box_valueChanged(self, value):
        self.slider.setValue(int(value * 1000))

        if not self.main_window.mocked:
            apply_voltage(self.main_window.device_name, value + offset)


class ApplyVoltagePage(BaseSetVoltagePage):
    def __init__(self, main_window):
        self.min_voltage = -2.5
        self.max_voltage = 2.5

        with self.init(main_window):
            super().__init__(
                'Apply Voltage',
                'About Applying Voltage',
                get_file('apply-voltage.md', 'desc', path=True).read_text(),
                280,
                (-2.5, 2.5)
            )

            self.desc.setMinimumHeight(345)

            self.slider.setMaximum(5000)
            self.slider.setValue(2499)

            text = (
                '<b>WARNING:</b> This voltage may not be applied accurately'
                ' due to limitations with the SEAL Kit.'
            )
            if warning_icon_loc := get_file('warning-icon.svg'):
                self.warning_label = LabelWithIcon(warning_icon_loc, text, indent=17)
            else:
                self.warning_label = QtWidgets.QLabel(text)
            sp_retain = self.warning_label.sizePolicy()
            sp_retain.setRetainSizeWhenHidden(True)
            self.warning_label.setSizePolicy(sp_retain)
            self.warning_label.setFixedHeight(32)
            self.warning_label.setObjectName('apply_voltage_warning_label')
            self.warning_label.setWordWrap(True)
            self.warning_label.hide()
            self.warning_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

            self.main_layout.insertWidget(3, self.warning_label)

    def set_min_and_max(self, voltage_offset: float):
        self.min_voltage = -round(5 - offset - voltage_offset, 3)
        self.max_voltage = -round(-offset - voltage_offset, 3)

        logger.info(f'self.min_voltage set to {self.min_voltage}.')
        logger.info(f'self.max_voltage set to {self.max_voltage}.')

        old_value = self.double_spin_box.value()

        self.double_spin_box.setRange(self.min_voltage, self.max_voltage)

        self.on_spin_box_valueChanged(old_value if old_value in self else 0)

    def is_high_or_low_voltage(self, voltage=None) -> bool:
        if voltage is None:
            voltage = self.double_spin_box.value()
        return voltage >= 0.75 * self.max_voltage or voltage <= 0.75 * self.min_voltage

    def __contains__(self, voltage: Union[int, float]) -> bool:
        return (
            voltage <= self.max_voltage
            and voltage >= self.min_voltage
        )

    @QtCore.pyqtSlot(float)
    def on_spin_box_valueChanged(self, value):
        value = round(value, 3)
        self.voltage_to_be_applied = value
        if self.is_high_or_low_voltage(value):
            self.warning_label.show()
        else:
            self.warning_label.hide()
        self.slider.setValue(round((value - self.min_voltage) * 1000))

    @QtCore.pyqtSlot(int)
    def on_slider_valueChanged(self, value):
        self.voltage_to_be_applied = round(value * 0.001 + self.min_voltage, 3)
        self.double_spin_box.setValue(self.voltage_to_be_applied)


class DarkCurrentPage(BasePage):
    def __init__(self, main_window):
        with self.init(main_window):
            self.bar = QtCharts.QBarSeries()
            self.bar.setLabelsVisible(True)
            self.bar.setLabelsPosition(
                QtCharts.QAbstractBarSeries.LabelsPosition.LabelsOutsideEnd
            )

            self.update_data()

            self.chart = QtCharts.QChart()
            self.chart.setTheme(QtCharts.QChart.ChartTheme.ChartThemeDark)
            self.chart.setTitle('Dark Current')
            title_font = QtGui.QFont()
            title_font.setPointSizeF(30)
            title_font.setWeight(700)
            title_font.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
            self.chart.setTitleFont(title_font)
            self.chart.addSeries(self.bar)

            self.chart.createDefaultAxes()
            for axis in self.chart.axes():
                axis.setGridLineVisible(False)
                axis.setMinorGridLineVisible(False)
            x_axis = self.chart.axes(QtCore.Qt.Orientation.Horizontal)[0]
            x_axis.setTitleText('Sample Number')

            y_axis = self.chart.axes(QtCore.Qt.Orientation.Vertical)[0]
            font = y_axis.titleFont()
            font.setHintingPreference(QtGui.QFont.HintingPreference.PreferNoHinting)
            y_axis.setTitleFont(font)
            y_axis.setTitleText('Volts')

            self.chart.legend().hide()
            self.chart.layout().setContentsMargins(0, 0, 0, 0)
            self.chart.setBackgroundRoundness(30)
            self.chart.setBackgroundBrush(QtCore.Qt.GlobalColor.black)

            self.set_y_axis_range()

            self.chart_view = QtCharts.QChartView(self.chart)
            self.chart_view.setObjectName('dark_current_chart_view')
            self.chart_view.setViewportUpdateMode(
                QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate
            )
            self.chart_view.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
            self.chart_view.setMinimumSize(630, 500)

            self.refresh_button = QtWidgets.QPushButton('Refresh')
            self.refresh_button.setObjectName('dark_current_refresh_button')
            self.refresh_button.setFocusPolicy(QtCore.Qt.FocusPolicy.TabFocus)
            self.refresh_button.setFixedWidth(100)

            self.chart_layout = QtWidgets.QVBoxLayout()
            self.chart_layout.addWidget(self.chart_view)
            self.chart_layout.setSpacing(30)
            self.chart_layout.addWidget(self.refresh_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            self.help_tab = QtWidgets.QLabel(get_file('dark-current.md', 'desc', path=True).read_text())
            self.help_tab.setTextFormat(QtCore.Qt.TextFormat.RichText)
            self.help_tab.setFixedWidth(help_tab_fixed_width)
            self.help_tab.setWordWrap(True)

            self.desc_layout = QtWidgets.QVBoxLayout()
            self.desc_layout.addWidget(self.help_tab)
            self.desc_layout.addStretch(40)
            self.desc_layout.setContentsMargins(help_tab_margins)

            self.main_layout = QtWidgets.QHBoxLayout()
            self.main_layout.addLayout(self.chart_layout)
            self.main_layout.addSpacing(30)
            self.main_layout.addLayout(self.desc_layout)
            self.main_layout.setContentsMargins(
                30, 30, 11, 11
            )

    def update_data(self):
        self.bar.clear()

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

        bar_set = QtCharts.QBarSet('Values')
        bar_set.setLabelColor(QtCore.Qt.GlobalColor.white)
        bar_set.setBrush(0x73C2FB)
        bar_set.setBorderColor(QtGui.QColor(0, 0, 0, 0))
        bar_set.append(samples)

        self.bar.append(bar_set)

        if max(samples) > 0.9:
            self.set_y_axis_range(max(samples) * 1.1)

        logger.info('Updated dark current readings.')

    def set_y_axis_range(self, upper: Union[float, int] = None):
        if upper is None:
            upper = max(self.samples) * 1.1
            if upper < 1:
                upper = 1

        if hasattr(self, 'chart'):
            self.chart.axes(QtCore.Qt.Orientation.Vertical)[0].setRange(0, upper)

    @property
    def samples(self):
        return [sample for sample in self.bar.barSets()[0]]

    @QtCore.pyqtSlot()
    def on_dark_current_refresh_button_clicked(self):
        self.update_data()

    def mousePressEvent(self, mouse_event: QtGui.QMouseEvent = None) -> None:
        if self.refresh_button.hasFocus() and not self.refresh_button.underMouse():
            self.setFocus(QtCore.Qt.FocusReason.OtherFocusReason)
        if mouse_event:
            super().mousePressEvent(mouse_event)


class ScanPage(BasePage):
    def __init__(self, main_window):
        with self.init(main_window):
            self.led_position_gen = LED_position_gen(start_at_zero=True)
            self.led_position = next(self.led_position_gen)

            self.scanned = []

            self.scan_index = None
            self.last_scanned = None

            self.scan_label = QtWidgets.QLabel('Scan')
            font = self.scan_label.font()
            font.setHintingPreference(QtGui.QFont.HintingPreference.PreferFullHinting)
            self.scan_label.setFont(font)
            self.scan_label.setObjectName('scan_page_header')

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

            self.create_bar_graph()

            self.bar_charts_tab.addTab(QtWidgets.QWidget(), '')

            self.scanning_progress_label = QtWidgets.QLabel('Scanning progress:')
            self.scanning_progress_label.hide()

            self.progress_bar = QtWidgets.QProgressBar()
            sp_retain = self.progress_bar.sizePolicy()
            sp_retain.setRetainSizeWhenHidden(True)
            self.progress_bar.setSizePolicy(sp_retain)
            self.progress_bar.hide()

            self.progress_bar_layout = QtWidgets.QHBoxLayout()
            self.progress_bar_layout.addWidget(self.scanning_progress_label)
            self.progress_bar_layout.addSpacing(10)
            self.progress_bar_layout.addWidget(self.progress_bar)

            self.notice_for_reading = QtWidgets.QLabel(
                'Even though it looks like nothing is happening, <b>data is still being read!</b> '
                "The reason you can't see anything happening on screen is because the values being "
                'read are zeros.'
            )
            sp_retain = self.notice_for_reading.sizePolicy()
            sp_retain.setVerticalPolicy(QtWidgets.QSizePolicy.Policy.Fixed)
            sp_retain.setRetainSizeWhenHidden(True)
            self.notice_for_reading.setSizePolicy(sp_retain)
            self.notice_for_reading.hide()

            self.start_button = QtWidgets.QPushButton('Start')
            self.start_button.setObjectName('start_button')

            self.save_button = QtWidgets.QPushButton('Save')
            self.save_button.setObjectName('save_button')
            self.save_button.setEnabled(False)
            self.save_button.hide()

            self.buttons_layout = QtWidgets.QHBoxLayout()
            self.buttons_layout.setSpacing(0)
            self.buttons_layout.addStretch(100)
            self.buttons_layout.addWidget(self.start_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            self.buttons_layout.addWidget(self.save_button, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

            self.bar_chart_layout = QtWidgets.QVBoxLayout()
            self.bar_chart_layout.setSpacing(0)
            self.bar_chart_layout.addWidget(self.scan_label, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)
            self.bar_chart_layout.addWidget(self.bar_charts_tab)
            self.bar_chart_layout.addSpacing(10)
            self.bar_chart_layout.addLayout(self.progress_bar_layout)
            self.bar_chart_layout.addSpacing(10)
            self.bar_chart_layout.addWidget(self.notice_for_reading, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
            self.bar_chart_layout.addSpacing(10)
            self.bar_chart_layout.addLayout(self.buttons_layout)

            self.help_tab = LinkHoverColorChange('#0078D8', '#777777', get_file('scan.md', 'desc', path=True).read_text())
            self.help_tab.setTextFormat(QtCore.Qt.TextFormat.RichText)
            self.help_tab.setOpenExternalLinks(True)
            self.help_tab.setFixedWidth(help_tab_fixed_width)
            self.help_tab.setWordWrap(True)

            self.desc_layout = QtWidgets.QVBoxLayout()
            self.desc_layout.addWidget(self.help_tab)
            self.desc_layout.addStretch(40)
            self.desc_layout.setContentsMargins(help_tab_margins)

            self.spacer2  = QtWidgets.QSpacerItem(
                20, 0, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum
            )

            self.main_layout = QtWidgets.QHBoxLayout()
            self.main_layout.addLayout(self.bar_chart_layout)
            self.main_layout.addSpacing(30)
            self.main_layout.addLayout(self.desc_layout)
            self.main_layout.setContentsMargins(
                30, 30, 11, 11
            )

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

    def create_bar_graph(self, index=0):
        # TODO: Figure out how to make bars matte

        graph_components = [
            QtDataVisualization.Q3DBars(),
            QtDataVisualization.QBar3DSeries(),
            numpy.zeros((8, 8)).view(TwoDQBarDataItem)
        ]

        bars: QtDataVisualization.Q3DBars = graph_components[0]
        bars.addSeries(graph_components[1])
        bars.rowAxis().setRange(0, 7)
        bars.columnAxis().setRange(0, 7)
        bars.setShadowQuality(QtDataVisualization.QAbstract3DGraph.ShadowQuality.ShadowQualityNone)
        theme = QtDataVisualization.Q3DTheme(QtDataVisualization.Q3DTheme.Theme.ThemeEbony)
        theme.setAmbientLightStrength(0.5)
        theme.setBaseColors([0x73C2FB])
        theme.setSingleHighlightColor(0xFFFFFF)
        bars.setActiveTheme(theme)
        graph_components.append(QtWidgets.QWidget.createWindowContainer(bars))

        self.bar_charts.append(graph_components)

        self.bar_charts_tab.insertTab(
            index,
            self.bar_charts[len(self.bar_charts) - 1][3],
            f'Scan {len(self.bar_charts)}'
        )

    @QtCore.pyqtSlot(int)
    def on_bar_charts_tab_currentChanged(self, tab: int):
        if tab + 1 == len(self.bar_charts_tab):
            self.create_bar_graph(tab)
            self.bar_charts_tab.setCurrentIndex(tab)
        elif tab == self.scan_index:
            self.scanning_progress_label.show()
            self.progress_bar.show()
            self.start_button.hide()
            self.save_button.show()
            self.save_button.setEnabled(False)
        elif tab in self.scanned:
            self.start_button.hide()
            self.save_button.show()
            self.save_button.setEnabled(True)
            self.notice_for_reading.hide()
        else:
            self.progress_bar.hide()
            self.scanning_progress_label.hide()
            self.notice_for_reading.hide()
            self.save_button.hide()
            self.start_button.show()
            self.start_button.setEnabled(self.scan_index is None)

    @QtCore.pyqtSlot()
    def on_start_button_clicked(self):
        if self.scan_index is None:
            # TODO: Move to another thread, this stops when app is moved around
            self.scan_index = scan_number = self.bar_charts_tab.currentIndex()

            self.scanning_progress_label.show()
            self.progress_bar.show()

            self.start_button.hide()
            self.save_button.show()

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
                    # samples = [dark_current] * 10
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
                else:
                    # Delay between all other LED flashes
                    QtTest.QTest.qWait(860 - 1 - computation_time * 1000)

            self.scanned.append(self.scan_index)
            self.scan_index = None

            self.save_button.setEnabled(True)
            self.notice_for_reading.hide()

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
