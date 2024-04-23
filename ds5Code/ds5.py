import time

# Constants
EMPTY_STATE_DIGITAL = [False, False, False, False, False, False, False, False]
N_CHANNELS = 8
mV_TO_VOLT = 1000.0
mS_TO_S = 1000.0


def reset_digital_output(digital_task):
    """
    Resets the digital output to its default state.
    
    Parameters:
    digital_task (Task): The digital task to be reset.
    """
    # Reset the digital output
    
    digital_task.write(EMPTY_STATE_DIGITAL, auto_start=True)


def select_channel(channel_no, electrode_selection_task):
    """
    Selects a channel for activation and writes the corresponding digital output to the electrode selection task.

    Args:
        channel_no (int): The channel number to be activated (between 1 and N_CHANNELS).
        electrode_selection_task: The electrode selection task object.

    Raises:
        ValueError: If the channel number is not between 1 and 8.

    Returns:
        None
    """
    input_to_d188 = [False] * N_CHANNELS
    if 1 <= channel_no <= N_CHANNELS:
        input_to_d188[channel_no - 1] = True
        print(
            f"Channel {channel_no} should be activated, with digital output {input_to_d188}"
        )
        # Covert to signal for D188
        # # Add digital channel
        electrode_selection_task.write(input_to_d188, auto_start=True)
    else:
        raise ValueError("Channel number must be between 1-8")
    

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
