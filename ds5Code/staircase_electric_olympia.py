import copy, time 
from collections import defaultdict
import time
from psychopy import event
import nidaqmx
from nidaqmx.constants import VoltageUnits
import time
from psychopy import visual, data
from IPython import embed as shell

# TODO: Check the conversion between the DS5 and national instruments, how much V=mA

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
def run_experiment():
    
    # Which channels to use
    used_channels = [1]

    # Contains stairfor all channels, each channel may have multiple stairs
    all_stairs = defaultdict(list)
    n_channels = len(used_channels)
    
    # create some info to store with the data
    info = {}
    info["startPoints"] = [100] # starting mikroAmperes
    info["nTrials"] = 50
    num_pulses = 10
    signal_duration = 25 # ms

    win = visual.Window([400, 400])

    # Create a staircase for each channel
    for channel_no in used_channels:
        
        # create stairs per channel
        stairs_per_channel = []
        
        for thisStart in info["startPoints"]:
            
            thisInfo = copy.copy(info)
            # now add any specific info for this staircase
            thisInfo["thisStart"] = (
                thisStart  # we might want to keep track of this
            )
            thisStair = data.StairHandler(
                startVal=thisStart,
                extraInfo=thisInfo,
                nTrials=50,
                nUp=3,
                nDown=1,
                minVal=10,
                maxVal=4000,
                #stepSizes=[5, 5, 2, 2, 1, 1],
                stepSizes=[3, 3, 2, 2, 1, 1],

            )
            stairs_per_channel.append(thisStair)
        all_stairs[channel_no] = stairs_per_channel

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

        # loop all channels, get the stairs as a list for that channel
        for channel, stairs in all_stairs.items():
            print(f"Staircase procedure in {channel}")
            select_channel(channel, digital_task)
            
            # Loop all trials
            for trialN in range(info["nTrials"]):

                # shuffle(stairs) #this shuffles 'in place' (ie stairs itself is changed, nothing returned)
                # then loop through our randomised order of staircases for this repeat
                # for thisStair in stairs:

                thisIntensity = next(thisStair)
                print(
                    "start=%.2f, current=%.4f"
                    % (thisStair.extraInfo["thisStart"], thisIntensity)
                )

                # Send stimulus to NI
                print(
                    f" Stimulus parameters are: channel: {channel}, amplitude: {thisIntensity}, signal_duration: {signal_duration}, pulse_number: {num_pulses}"
                )
                # Reset the analog channel
                ds5_task.write(0, auto_start=True)

                # Give shock
                give_shock(
                    thisIntensity,
                    signal_duration,
                    num_pulses,
                    ds5_task,
                )

                # Reset the analog channel to 0 again
                ds5_task.write(0, auto_start=True)
                keys = (
                    event.waitKeys()
                )  # (we can simulate by pushing left for 'correct')
                if "d" in keys:
                    wasCorrect = True
                    print("Stimulus was detected")
                else:
                    wasCorrect = False

                thisStair.addData(
                    wasCorrect
                )  
                
    # save data (separate pickle and txt files for each staircase)
    dateStr = time.strftime("%b_%d_%H%M", time.localtime())  # add the current time
    for thisStair in stairs:
        # create a filename based on the subject and start value
        #filename = "%s start%.2f %s" % (
        #    #thisStair.extraInfo["observer"],
        #    thisStair.extraInfo["thisStart"],
        #    dateStr,
        #)
        thisStair.saveAsExcel('test')
        #shell()
#
#    with open(filename + ".psydat", "rb") as f:
#        data = pickle.load(f)


run_experiment()
    
    