from typing import Union
from .constants import offset

import nidaqmx

def apply_voltage(device_name: str, voltage: Union[float, int] = offset):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(f'{device_name}/ao0', min_val=0, max_val=5)
        task.write(voltage)
