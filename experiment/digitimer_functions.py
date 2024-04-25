"""
Tracking touch experiment: Pupil response to prediction errors in touch
"""

import copy, time 
from collections import defaultdict
from psychopy import core, visual, event, gui, monitors
import nidaqmx
from nidaqmx.constants import VoltageUnits
from psychopy import visual, data
from IPython import embed as shell # for olympia debugging only

# TODO: Check the conversion between the DS5 and national instruments, how much V=mA

"""
PARAMETERS
"""
# DIGITIMER
EMPTY_STATE_DIGITAL = [False, False, False, False, False, False, False, False]
N_CHANNELS = 8
mV_TO_VOLT = 1000.0
mS_TO_S = 1000.0
N_TRIALS_PER_CHANNEL = 2


def reset_digital_output(digital_task):
    digital_task.write(EMPTY_STATE_DIGITAL, auto_start=True)


def give_shock(amplitude, duratiton, amountPulse, analog_task):
    """
    Generates a shock waveform with the given parameters.

    Parameters:
    amplitude (float): The amplitude of the shock waveform in millivolts.
    duratiton (float): The duration of each pulse in milliseconds.
    amountPulse (int): The number of pulses to generate.
    analog_task: The analog task object used to write the waveform.

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


def select_channel(channel_no, electrode_selection_task):
    """
    Activates the specified channel and sets the digital output for the D188 device.

    Args:
        channel_no (int): The channel number to activate. Must be between 1 and N_CHANNELS.
        electrode_selection_task: The task object for electrode selection.

    Raises:
        ValueError: If the channel number is not within the valid range.

    Returns:
        None
    """
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


#1mv=1mikroA
def administer_touch(channel=1, this_intensity):

    num_pulses = 10
    signal_duration = 25 # ms

    # Create analog channel for stm parameters and digital channel for electrode selection
    with nidaqmx.Task() as ds5_task, nidaqmx.Task() as digital_task:

        # DAQmx Configure Code add analog and digital channels
        ds5_task.ao_channels.add_ao_voltage_chan(
            "Dev2/ao0", min_val=-4.0, max_val=4.0, units=VoltageUnits.VOLTS
        )
        digital_task.do_channels.add_do_chan(
            "Dev2/port0/line0:7",
            line_grouping=nidaqmx.constants.LineGrouping.CHAN_PER_LINE,
        )

        select_channel(channel, digital_task)

        # Send stimulus to NI
        print(
            f" Stimulus parameters are: channel: {channel}, amplitude: {this_intensity}, signal_duration: {signal_duration}, pulse_number: {num_pulses}"
        )
        # Reset the analog channel
        ds5_task.write(0, auto_start=True)

        # Give shock
        give_shock(
            this_intensity,
            signal_duration,
            num_pulses,
            ds5_task,
        )
                