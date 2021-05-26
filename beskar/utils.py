from typing import Generator, Tuple, Union
from .constants import offset

import nidaqmx

def apply_voltage(device_name: str, voltage: Union[float, int] = offset):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(f'{device_name}/ao0', min_val=0, max_val=5)
        task.write(voltage)

def LED_position_gen(start_at_zero=False) -> Generator[Tuple[int, int], None, None]:
    offset = 1 if start_at_zero else 0

    row_pattern = [7, 2, 5, 4, 3, 6, 1, 8]
    column_pattern = [8, 2, 6, 7, 3, 5, 1]

    yield (2 - offset, 4 - offset)
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
