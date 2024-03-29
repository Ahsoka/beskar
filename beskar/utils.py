from typing import Callable, Generator, Tuple, Union, Literal, Any, List
from PyQt6.QtDataVisualization import QBarDataItem
from nidaqmx._lib import DaqNotFoundError
from contextlib import contextmanager
from PyQt6.QtCore import QMetaObject
from nidaqmx.system import System
from .constants import offset

import itertools
import logging
import pathlib
import nidaqmx
import numpy
import re

logger = logging.getLogger(__name__)

def apply_voltage(device_name: str, voltage: Union[float, int] = offset):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(f'{device_name}/ao0', min_val=0, max_val=5)
        task.write(voltage)

    logger.info(f'{voltage} has been applied to the SEAL kit.')

def LED_position_gen(start_at_zero: bool = False) -> Generator[Union[Tuple[int, int], Tuple[int, int, None]], None, None]:
    offset = 1 if start_at_zero else 0

    row_pattern = [7, 2, 5, 4, 3, 6, 1, 8]
    column_pattern = [8, 2, 6, 7, 3, 5, 1]

    yield (2 - offset, 4 - offset, None)
    yield (2 - offset, 4 - offset)
    for row in row_pattern[2:]:
        yield (row - offset, 4 - offset)
    for column in column_pattern:
        for row in row_pattern:
            yield (row - offset, column - offset)

    while True:
        yield (7 - offset, 4 - offset)
        for column in [4] + column_pattern:
            for row in row_pattern:
                yield (row - offset, column - offset)

def interact_with_LEDs(device_name: str, interaction: Literal['on', 'off', 'on&off']):
    if interaction not in {'on', 'off', 'on&off'}:
        raise ValueError(f"interaction must be 'on', 'off', or 'on&off', not '{interaction}'")

    logger.info(f'The LEDs in the SEAL kit were turned {interaction}.')

    with nidaqmx.Task() as task:
        task.do_channels.add_do_chan(f'{device_name}/port0/line0')
        if interaction == 'on':
            task.write(False)
        elif interaction == 'off':
            task.write(True)
        elif interaction == 'on&off':
            task.write(False)
            task.write(True)

def get_number_of_devices(system=True, drivers=False):
    errors  = (FileNotFoundError, DaqNotFoundError)
    has_drivers = True
    try:
        from __main__ import PyInstallerImportError
        errors += (PyInstallerImportError,)
    except ImportError:
        pass
    the_system = System.local()
    try:
        num_of_devices = len(the_system.devices)
    except errors:
        num_of_devices = 0
        has_drivers = False
    if system and drivers:
        return the_system, num_of_devices, has_drivers
    elif system:
        return the_system, num_of_devices
    elif drivers:
        return has_drivers, num_of_devices
    else:
        return num_of_devices

def get_file(file_path: str, dir='images', path=False) -> Union[pathlib.Path, str, None]:
    try:
        icon_path = next(pathlib.Path('.').glob(f'**/{dir}/{file_path}'))
        if path:
            return icon_path
        else:
            return str(icon_path)
    except StopIteration:
        # If this happens, somehow the icon was deleted from the install folder
        # TODO: Connect to internet and reinstall missing asset
        # NOTE: Reinstalling missing asset is more difficult that initially
        # presumed since it will require writing to a location that requires
        # escalated privileges to write to. Perhaps this could be solved by saving
        # the assets in non escalated privileges folder such as %appdata%
        logger.warning(f'{file_path} was not detected, may be fatal.')

def get_folder(folder: Union[str, pathlib.Path], path: bool = True):
    if isinstance(folder, str):
        folder = pathlib.Path(folder)

    if not folder.exists():
        folder = pathlib.Path('beskar') / folder

    if folder.exists():
        if path:
            return folder
        else:
            return str(folder)

    logger.warning(f'{folder} could not be found, may be fatal.')

def sort_frames(
    folder: pathlib.Path,
    glob: str, key: Callable[[pathlib.Path], Any] = None,
    cycler: bool = True
):
    if key is None:
        frame_number = re.compile(r'\d+')
        key = lambda path: int(frame_number.search(path.name)[0])

    sorted_frames = sorted(folder.glob(glob), key=key)
    if cycler:
        return itertools.cycle(sorted_frames)
    else:
        return sorted_frames

def error_to_exc_tuple(error: Exception):
    return (type(error), error, error.__traceback__)


class TwoDQBarDataItem(numpy.ndarray):
    def tolist(self, convert_to_bar_data=False) -> Union[List[List[QBarDataItem]], List[List[int]]]:
        if convert_to_bar_data:
            return [list(
                map(lambda item: QBarDataItem(item), listt)
            ) for listt in super().tolist()]
        else:
            return super().tolist()

    def __setitem__(self, key, value) -> None:
        current_value = self[key]
        if not hasattr(self, 'last_values_written'):
            self.last_values_written = []
        if current_value != 0:
            value = (current_value + value) / 2
        self.last_values_written.append(value)

        super().__setitem__(key, value)

    def last_values_zero(self):
        if not hasattr(self, 'last_values_written'):
            self.last_values_written = []

        return (all(map(lambda item: item == 0, self.last_values_written[-4:]))
                and len(self.last_values_written[-4:]) >= 4)


class BaseInteractable:
    @contextmanager
    def init(self, main_window=None):
        self.main_window = main_window
        self.super_()
        yield
        self.setLayout(self.main_layout)
        QMetaObject.connectSlotsByName(self)
