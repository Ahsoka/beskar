from typing import Union
from .constants import offset

import nidaqmx

def apply_voltage(device_name: str, voltage: Union[float, int] = offset, min_val: int = 0, max_val: int = 5):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(
            f'{device_name}/ao0',
            min_val=min_val,
            max_val=max_val
        )
        task.write(voltage)
