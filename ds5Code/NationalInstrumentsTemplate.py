import os
import platform
import time
from psychopy import core, clock, visual, event, sound
import my  # import your own functions
import nidaqmx
from nidaqmx import Task
from nidaqmx.constants import VoltageUnits, TerminalConfiguration, Edge
import sys
import time
import random

# print info
# print('python version: {}'.format(platform.python_version()))
# print('psychopy version: {}'.format(psychopy.__version__))
# print('Using {}(with {}) for sounds'.format(sound.audioLib, sound.audioDriver))

## Setup Section
# win = visual.Window([800, 600], fullscr=False, monitor="testMonitor", units='cm')
# Constants
EMPTY_STATE_DIGITAL = [False, False, False, False, False, False, False, False]
N_CHANNELS = 8
mV_TO_VOLT = 1000.0
mS_TO_S = 1000.0
N_TRIALS_PER_CHANNEL = 2
AMP_INC = 100 
DUR_INC = 2

def reset_digital_output(digital_task):
    digital_task.write(EMPTY_STATE_DIGITAL, auto_start=True)


def give_shock(amplitude, duratiton, amountPulse, analog_task):
    """
    Gives a shock with the specified amplitude, duration, and number of pulses.

    Parameters:
    amplitude (float): The amplitude of the shock in millivolts.
    duratiton (float): The duration of each pulse in milliseconds.
    amountPulse (int): The number of pulses to deliver.
    analog_task (object): The analog task object used for writing the shock signal.

    Returns:
    None
    """
    # win.flip()
    amplitude = amplitude / mV_TO_VOLT
    duratiton = duratiton / mS_TO_S
    for i in range(amountPulse):
        analog_task.write(amplitude, auto_start=True)
        time.sleep(duratiton)
        analog_task.write(-amplitude, auto_start=True)
        time.sleep(duratiton)
    analog_task.write(0)


def get_pulse_congfig(analog_task, digital_task):
    try:
        channel = my.getString2(win, "Enter channel to simulate (1-8):")
        if channel == "escape":
            quit_app(analog_task, digital_task)
        else:
            channel = int(channel)
        amp_of_pulse = my.getString2(win, "Give AMPLITUDE pulse(mV):")
        if amp_of_pulse == "escape":
            quit_app(analog_task, digital_task)
        else:
            amp_of_pulse = float(amp_of_pulse) / mV_TO_VOLT  # convert from mV to V

        duratiton_of_pulse = my.getString2(win, "Give duration of pulse(mS):")
        if duratiton_of_pulse == "escape":
            quit_app(analog_task, digital_task)
        else:
            duratiton_of_pulse = (
                float(duratiton_of_pulse) / mS_TO_S
            )  # convert from mS to S
        number_of_pulses = int(my.getString2(win, "Give NUMBER OF pulses:"))
        if number_of_pulses == "escape":
            quit_app(analog_task, digital_task)
    except ValueError as err:
        print(err)
        quit_app(analog_task, digital_task)
    return channel, amp_of_pulse, duratiton_of_pulse, number_of_pulses



def select_channel(channel_no, electrode_selection_task):
    input_to_d188 = [False] * N_CHANNELS
    if 1 <= channel_no <= N_CHANNELS:
        input_to_d188[channel_no - 1] = True
        print(
            f"Channel {channel_no} should be activated, with digital output {input_to_d188}"
        )
    else:
        raise ValueError("Channel number must be between 1-8")

    # Covert to signal for D188
    # # Add digital channel
    electrode_selection_task.write(input_to_d188, auto_start=True)


def main():

    with nidaqmx.Task() as ds5_task, nidaqmx.Task() as digital_task:

        # DAQmx Configure Code
        ds5_task.ao_channels.add_ao_voltage_chan(
            "Dev2/ao0", min_val=-4.0, max_val=4.0, units=VoltageUnits.VOLTS
        )
        digital_task.do_channels.add_do_chan(
            "Dev2/port0/line0:7",
            line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE,
        )

        my.getCharacter(win, "start calibration")

        while True:
            channel, amp_of_pulse, duratiton_of_pulse, number_of_pulses = (
                get_pulse_congfig(ds5_task, digital_task)
            )
            try:
                select_channel(channel, digital_task)
            except ValueError as e:
                print(e)
                quit_app(ds5_task, digital_task)
            # Reset the analog channel
            ds5_task.write(0, auto_start=True)

            # Give shock
            give_shock(amp_of_pulse, duratiton_of_pulse, number_of_pulses, ds5_task)

            # Reset the analog channel to 0 again
            ds5_task.write(0, auto_start=True)


def quit_app(analog_task=None, digital_task=None):
    if analog_task is not None:
        analog_task.write(0, auto_start=True)
        analog_task.stop()
    if digital_task is not None:
        digital_task.write(EMPTY_STATE_DIGITAL, auto_start=True)
        digital_task.stop()
    ## Closing Section
    # win.close()
    core.quit()
    sys.exit(0)

# Select a stimulation parameter set, amplitude, duration and number of pulses
# wait for a channel selection, send stimulation to that channel
def experiment_pilot():
    n_trials = 50
    # Starting Parameters for the simulus
    stim_parameters = {
        "amp_of_pulse": 500,
        "duration_of_pulse": 1,
        "number_of_pulses": 1,
    }
   
    used_channels = [1, 2, 3, 4, 5] 
    with nidaqmx.Task() as ds5_task, nidaqmx.Task() as digital_task:
        # DAQmx Configure Code
        ds5_task.ao_channels.add_ao_voltage_chan(
            "Dev2/ao0", min_val=-4.0, max_val=4.0, units=VoltageUnits.VOLTS
        )
        digital_task.do_channels.add_do_chan(
            "Dev2/port0/line0:7",
            line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE,
        )
        for i in range(n_trials):
            channel = input(f"Select channel from {used_channels}: ")
            change_amplitude = input(f"w to increase s to decrease the amplitude by {AMP_INC} mV ")
            change_duration = input(f'a to deacrease d to increase the duration by {DUR_INC} mV ')
            
            if change_amplitude.lower() == 'w' and  stim_parameters["amp_of_pulse"] < 5000:
                stim_parameters["amp_of_pulse"] += AMP_INC
            elif change_amplitude.lower() == 's' and  stim_parameters["amp_of_pulse"] > AMP_INC:
                stim_parameters["amp_of_pulse"] -= AMP_INC
            
            if change_duration.lower() == 'a' and stim_parameters["duration_of_pulse"] > DUR_INC:
                stim_parameters["duration_of_pulse"] -= DUR_INC
            elif change_duration.lower() == 'd' and stim_parameters["duration_of_pulse"] < 500:
                stim_parameters["duration_of_pulse"] += DUR_INC
                 
            try:
                channel = int(channel)
                select_channel(channel, digital_task)
            except ValueError as e:
                print(e)
                quit_app(ds5_task, digital_task)

            # Reset the analog channel
            ds5_task.write(0, auto_start=True)
            
            print(stim_parameters)
            # Give shock
            give_shock(
                stim_parameters["amp_of_pulse"],
                stim_parameters["duration_of_pulse"],
                stim_parameters["number_of_pulses"],
                ds5_task,
            )
            # Reset the analog channel to 0 again
            ds5_task.write(0, auto_start=True)

if __name__ == "__main__":
    # experiment_pilot()
    # 1V = 1mA
    # 1000ohm * 0.5mA = 500mV 
    # 10 duration means 100ms
    # 3000mV 3V
    # 3mA
    # 1.5V
    stim_parameters = {
        "amp_of_pulse": 3000,
        "duration_of_pulse": 10,
        "number_of_pulses": 1,
    }
    # just give shock at some amplitude
    with nidaqmx.Task() as ds5_task, nidaqmx.Task() as digital_task:
        # DAQmx Configure Code
        ds5_task.ao_channels.add_ao_voltage_chan(
            "Dev2/ao0", min_val=-4.0, max_val=4.0, units=VoltageUnits.VOLTS
        )
        digital_task.do_channels.add_do_chan(
            "Dev2/port0/line0:7",
            line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE,
        )
        channel = 1
        try:
            channel = int(channel)
            select_channel(channel, digital_task)
        except ValueError as e:
            print(e)
            quit_app(ds5_task, digital_task)

        # Reset the analog channel
        ds5_task.write(0, auto_start=True)
        
        # Give shock
        give_shock(
            stim_parameters["amp_of_pulse"],
            10,
            10,
            ds5_task,
        )
        # Reset the analog channel to 0 again
        ds5_task.write(0, auto_start=True)