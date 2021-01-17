import nidaqmx

task = nidaqmx.Task()
task.do_channels.add_do_chan('Dev1/port0/line0')
task.start()

# Initiate LED flashing
task.write(False)

# Stop LED flashing (with some delay)
task.write(True)

task.stop()
task.close()
