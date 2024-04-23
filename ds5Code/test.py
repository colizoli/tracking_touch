import os
import platform

import psychopy
from psychopy import core, clock, visual, event, sound
import my  # import your own functions
from nidaqmx import Task
from nidaqmx.constants import VoltageUnits, TerminalConfiguration, Edge

def giveShock(amplitude, duratiton, amountPulse, analog_task):
    for i in range(amountPulse):
        analog_task.write(amplitude, auto_start=True)
        # core.wait(time)
        time.sleep(duratiton/1000)
        analog_task.write(-amplitude, auto_start=True)
        time.sleep(duratiton/1000)

# National Instruments
freq = 100.0  # Hz
analog_task = Task()
amp = 2
duratiton = 100
amount = 100


# DAQmx Configure Code
analog_task.ao_channels.add_ao_voltage_chan("Dev2/ao0", min_val=-4.0, max_val=4.0, units=VoltageUnits.VOLTS)
# analog_task.timing.cfg_samp_clk_timing(freq, source='')
analog_task.write(0,auto_start=True)

giveShock(amp,duratiton,amount,analog_task)
analog_task.write(0,auto_start=True)
analog_task.stop()
analog_task.close()

