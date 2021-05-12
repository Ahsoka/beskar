import nidaqmx

def apply_voltage(device_name, voltage=2.5, min_val=0, max_val=5):
    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(
            f'{device_name}/ao0',
            min_val=min_val,
            max_val=max_val
        )
        task.write(voltage)
