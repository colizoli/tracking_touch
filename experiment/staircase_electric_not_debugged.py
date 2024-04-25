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

# response buttons
detection_button = 'D' # when stimulus is detected, otherwise
nothing_button = 'J'

# Screen-specific parameters lab B.00.80A
# scnWidth, scnHeight = (1920, 1080)
scnWidth, scnHeight = (800, 600) # for debugging
screen_width        = 53.5 # centimeters
screen_dist         = 58.0
grey = [128,128,128]
fh  = 50  # fixation cross height
ww = 1000 # wrap width of instructions text

# Set-up window:
mon = monitors.Monitor('myMac15', width=screen_width, distance=screen_dist)
mon.setSizePix((scnWidth, scnHeight))
win = visual.Window(
    (scnWidth, scnHeight),
    color = grey,
    colorSpace = 'rgb255',
    monitor = mon,
    fullscr = False,
    units = 'pix',
    allowStencil = True,
    autoLog = False)
win.setMouseVisible(False)
    
    
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


def initialize_subject():
    # initialize subject, logfile folder, instructions etc.
    
    # Get subject number
    g = gui.Dlg()
    g.addField('Subject Number:')
    g.show()
    subject_ID = int(g.data[0])
    
     ## Create LogFile folder cwd/LogFiles
    cwd = os.getcwd()
    logfile_dir = os.path.join(cwd, 'sourcedata', 'sub-{}'.format(subject_ID))
    if not os.path.isdir(logfile_dir):
        os.makedirs(logfile_dir)
    
    # Set-up stimuli and timing
    welcome_txt = "Touch detection\
    \nWe will determine your individual threshold for feeling touch.\
    \nYour task is to indicate when you feel any sensation on either of your 3 fingers.\
    \nIf you feel any sensation at all, press {}. If you feel nothing at all, then press {}\
    \n\nThis procedure will take a couple of minutes for each finger.\
    \n\n<Press any button to BEGIN>".format(detection_button, nothing_button)
    
    stim_instr      = visual.TextStim(win, color='black', pos=(0.0, 0.0), wrapWidth=ww) 
    
    # Welcome instructions
    stim_instr.setText(welcome_txt)
    stim_instr.draw()
    win.flip()
    core.wait(0.25)
    event.waitKeys()
        
    return subject_ID, logfile_dir
    

#1mv=1mikroA
def run_experiment():

    subject_ID, logfile_dir = initialize_subject()
    stim_finger = visual.TextStim(win, text='Finger',color='black', pos=(0.0, 0.0), height=fh)
    stim_fix    = visual.TextStim(win, text='+',color='black', pos=(0.0, 0.0), height=fh)
    stim_touch  = visual.TextStim(win, text='Did you feel any touch? \n\n Yes ("D") No ("J")',color='black', pos=(0.0, 0.0), height=fh)
    
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
                stepSizes=[3, 3, 2, 2, 1, 1], # 5 was too painful

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
        
            stim_finger.setText("Finger {}".format(channel_no))
            stim_finger.draw()
            win.flip()
            core.wait(1)
            
            # Loop all trials
            for trialN in range(info["nTrials"]):

                # shuffle(stairs) #this shuffles 'in place' (ie stairs itself is changed, nothing returned)
                # then loop through our randomised order of staircases for this repeat
                # for thisStair in stairs:
                
                stim_fix.draw()
                win.flip()
                core.wait(0.25)
                
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
                
                stim_touch.draw()
                win.flip()
                
                # Reset the analog channel to 0 again
                ds5_task.write(0, auto_start=True)
                keys = (
                    event.waitKeys()
                )  # (we can simulate by pushing left for 'correct')
                if detection_button in keys:
                    wasCorrect = True
                    print("Stimulus was detected")
                else:
                    wasCorrect = False

                thisStair.addData(
                    wasCorrect
                )  
                
    # save data (separate txt file for each staircase)
    for idx,thisStair in enumerate(stairs):
        thisStair.saveAsExcel(os.path.join(logfile_dir, 'sub-{}_staircase_{}'.format(subject_ID, idx))) # there should be a separate staircase for each finger


run_experiment()
    
    