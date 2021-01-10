import nidaqmx.system
system = nidaqmx.system.System.local()
device = system.devices['Dev1']
print(device)
print(device.product_type)
print(device.terminals)
print(device.ao_voltage_rngs)
print(device.ai_voltage_rngs)
