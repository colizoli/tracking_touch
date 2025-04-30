"""
Tracking touch experiment VERSION 2: Pupil response to prediction errors in touch
Python 3.9

O.Colizoli 2025

Notes:
SOLENOID CODES (left to right): 3210
RESPONSE KEYES: index->left(1), middle->down(2), ring->right(3)

"""

######## DESIGN ########
# Each trial:
# phase 1 baseline
# phase 2 touch 1 onset
# phase 3 response
# phase 4 touch 2 (feedback onset)
# phase 5 ITI onset

# Import necessary modules
from psychopy import core, visual, event, gui, monitors
import random
import numpy as np
import pandas as pd
import os, time  # for paths and data
from IPython import embed as shell # for Olympia debugging only, comment out if crashes
import solenoid_functions
global serial_port

# mode
debug_mode = True # fewer trials
eye_mode = False
touch_mode = False

if touch_mode:
    serial_port = solenoid_functions.define_serial_port()

"""
PARAMETERS
"""
# hard_path = os.path.join("d:", "users", "Isabel", "experiment2")
# os.chdir(hard_path)

hard_path = os.path.join(os.getcwd())
os.chdir(hard_path)

# Screen-specific parameters lab B.00.80A
if debug_mode:
    scnWidth, scnHeight = (800, 600) # for debugging
else:
    scnWidth, scnHeight = (1920, 1080)
screen_width        = 53.5 # centimeters
screen_dist         = 58.0
grey = [128,128,128]

# response buttons
buttons = ['left', 'down', 'right'] # top, middle, bottom
button_names = ['top', 'middle' , 'bottom']

# Set trial conditions and randomize stimulus list
REPS_PER_BLOCK = 7 # times to repeat trial unit full experiment (3 fingers x 7 reps = 21 trials per block)
MIN_BLOCKS = 5     # minimum number of blocks to reach desired accuracy level
EXTRA_BLOCKS = 4   # maximum number of blocks to reach desired accuracy level
FLIP_BLOCKS = 5    # number of blocks to administer after flipping the hand
# accuracy
THRESH_ACC = 0.70   # desired accuracy level before flipping the hand

# initialize counters
trial_num     = 1 # count all trials
block_counter = 1 # count all blocks
flip          = 0 # start with hand upwards
get_acc       = 0 # check accuracy

if debug_mode:
    reps      = 1 # debug mode reps
else:
    reps      = REPS_PER_BLOCK

# Timing in seconds
t_baseline  = 1   # baseline pupil
t_touch     = 1.5 # stimulus duration touch1
t_response  = 3   # maximum response window
t_delay     = 3.5 # after response
t_feedback  = 1.5 # stimulus duration touch2
t_ITI       = [3.5,5.5] # inter-trial interval

# touch distributions
# SOLENOID CODES (left to right: 3210)
# NOTE: solution: index-ring, middle-middle, ring-index

touch1      = [1,2,3] # index, middle, ring
touch2      = [
    [1,2,3,3,3,3,3,3,3,3],  # ring
    [1,2,2,2,2,2,2,2,2,3], # middle
    [1,1,1,1,1,1,1,1,2,3], # index
           ]

# Size  screen 1920 x 1080, units in pixels
fh  = 50  # fixation cross height
ww = 1000 # wrap width of instructions text

""" 
Initialize the psychopy experiment
"""
# Get subject number
g = gui.Dlg()
g.addField('Subject Number:')
g.show()
try:
    subject_ID = g.data[0]
except:
    subject_ID = list(g.data.values())[0]

subject_id_num = int(subject_ID) # register as interger

# Determine initial hand posture: even = up (0), odd = down (1)
if subject_id_num % 2 == 0:
    direction_hand = 'UPWARDS'
else:
    direction_hand = 'DOWNWARDS'
    
 ## Create LogFile folder cwd/LogFiles
logfile_dir = os.path.join( 'sourcedata', 'sub-{}'.format(subject_ID))
if not os.path.isdir(logfile_dir):
    os.makedirs(logfile_dir)

## output file name with time stamp prevents any overwriting of data
timestr = time.strftime("%Y%m%d-%H%M%S") 
output_filename = os.path.join(logfile_dir,'sub-{}_task-touch_prediction2_events_{}.csv'.format(subject_ID,timestr ))
cols = ['subject', 'block', 'initial_hand', 'flip', 'trial_num', 'touch1', 'touch2', 'response', 'correct', 'RT', 'ITI', 'onset_touch1', 'onset_touch2', 'nuisance_rts1', 'nuisance_rts2']
DF = pd.DataFrame(columns=cols)
    
# Set-up window:
mon = monitors.Monitor('myMac15', width=screen_width, distance=screen_dist)
mon.setSizePix((scnWidth, scnHeight))
win = visual.Window(
    (scnWidth, scnHeight),
    color = grey,
    colorSpace = 'rgb255',
    monitor = mon,
    fullscr = not debug_mode,
    units = 'pix',
    allowStencil = True,
    autoLog = False)
win.setMouseVisible(False)

# Set-up stimuli and timing
instr1_txt = "Touch prediction\
\nYou will be touched on your finger(s) twice in a row.\
\nYOUR TASK IS TO PREDICT ON WHICH FINGER THE 2ND TOUCH WILL BE.\
\n\nThe probabilities of the 2nd touch do not change over the course of the experiment.\
\nFocus on being maximally correct in your responses.\
\nIn other words, try to correctly guess on which finger the 2nd touch will happen as much as possible.\
\n\n<Press any button to CONTINUE INSTRUCTIONS>"

instr2_txt = "Touch prediction\
\nGive your prediction for the finger of the 2nd touch when you see the DIAMOND symbol appear.\
\n\nAfter the first touch, press the Index/ Middle/ Ring finger (Left/ Down /Right) key to indicate your prediction.\
\n\nMaintain fixation on the '+' in the center of the screen for the duration of the experiment.\
\nIn between blocks you will have a break during which you can move your hand/head/eyes.\
\nBlink as you normally would, but try not to move your head during the experiment.\
\n\n<Press any button to CONTINUE INSTRUCTIONS>"

instr3_txt = "Now the actual experiment will begin!\
\nPlace your hand so it is facing {}\
\n\nThere will be 9-10 blocks in total (~5 min each), each with several trials.\
\nIn between the blocks, you can take a break to move your head.\
\n\nWhen you are ready to continue with the next block,\
\nplace your head back in the chin rest and fixate on the dot at the center of the screen.\
\n\nAgain the keys are Index /Middle /Ring finger: Left/ Down /Right arrow keys.\
\n\n<Press any button to BEGIN the EXPERIMENT>".format(direction_hand)

normal_break_text = "Take a short break!\
\n\n Keep your left hand facing {}. \
\n\nAgain the keys are Index/ Middle/ Ring finger: Left/ Down /Right arrow keys.\
\n\nPush any button when you are ready to CONTINUE.".format(direction_hand)
 
stim_instr   = visual.TextStim(win, text=instr1_txt, color='black', pos=(0.0, 0.0), wrapWidth=ww)

stim_size = (40,40)
stim_fix    = visual.ImageStim(win, image=os.path.join('stimuli', 'plus.png'), size=stim_size)
stim_touch  = visual.ImageStim(win, image=os.path.join('stimuli', 'kruis.png'), size=stim_size)
stim_resp   = visual.ImageStim(win, image=os.path.join('stimuli', 'ruit.png'), size=stim_size)
stim_ITI    = visual.ImageStim(win, image=os.path.join('stimuli', 'plus.png'), size=stim_size)

### CONFIG & CALIBRATION EYE-TRACKER ###
if eye_mode:
    import funcs_pylink3 as eye
    task = 'touch_prediction'
    eye.config(subject_ID,task)
    eye.run_calibration(win, scnWidth, scnHeight)
    eye.start_recording()
    eye.send_message('subject_ID sub-{} task-{} timestamp {}'.format(subject_ID, task ,timestr))

# Welcome instructions
stim_instr.setText(instr1_txt)
stim_instr.draw()
win.flip()
core.wait(0.25)
event.waitKeys()

stim_instr.setText(instr2_txt)
stim_instr.draw()
win.flip()
core.wait(0.25)
event.waitKeys()

# Instructions depending on initial hand position
stim_instr.setText(instr3_txt)
stim_instr.draw()
win.flip()
core.wait(0.25)
event.waitKeys()

onset_tria11 = np.nan
onset_touch1 = np.nan
onset_touch2 = np.nan


def check_keys(this_clock):
    """ Check if any buttons were pressed outside of the response window. 
        Quit if "q" or "escape" was pressed.
    """
    # For quitting early
    keys = event.getKeys(timeStamped=this_clock) # clear the key buffer
    if keys:
        for k in keys:
            if ('q' in k) or ('escape' in k): # q quits the experiment
                if eye_mode:
                    eye.stop_skip_save()
                core.quit()
        else:
            return keys # save all button press timings for cleaning data


def update_break_text(type_break, direction_hand):
    """Updates the break texts based on hand direction.
        Returns break_text
    """
    
    first_flipped_break_text = "Take a short break!\
    \n\nFROM NOW ON, POSITION YOUR LEFT HAND SO IT IS FACING {}. \
    \n\nAgain the keys are Index/ Middle/ Ring finger: Left/ Down /Right arrow keys.\
    \nBlink as you normally would, but try not to move your head during the experiment.\
    \n\nPush any button when you are ready to CONTINUE.".format(direction_hand)

    flipped_break_text = "Take a short break!\
    \n\n Keep your left hand facing {}. \
    \n\nAgain the keys are Index/ Middle/ Ring finger: Left/ Down /Right arrow keys.\
    \n\nPush any button when you are ready to CONTINUE.".format(direction_hand)
    
    if type_break == 'first':
        break_text = first_flipped_break_text
    else:
        break_text = flipped_break_text
    return break_text
    

# define break and block functions
def present_break(break_text):
    """ Present a break of the experiment with the given text.
    """    
    if eye_mode:
        eye.pause_stop_recording() # pause recording
    stim_instr.setText(f"Take a short break! \
    \nYou have completed {block_counter - 1} blocks")
    stim_instr.draw()
    win.flip()
    core.wait(3)
    # Break instructions continue
    stim_instr.setText(break_text)
    stim_instr.draw()
    win.flip()
    event.waitKeys()
    # Drift correction, when subject moves their head during breaks
    if eye_mode:
        eye.run_drift_correction(win, scnWidth, scnHeight)
    print('End break')
    
    
def present_block():
    """ Present a block of the experiment.
    """
    global trial_num
    global block_counter
    nuisance_rts = []                       # empty vector for nuisance
    
    # shuffle trials within each block
    trials = touch1*reps
    np.random.shuffle(trials) 
    print(trials)
    
    # Wait a few seconds before first trial to stabilize gaze
    stim_fix.draw()
    win.flip()
    core.wait(3) 

    #### TRIAL LOOP ### --> add the intervals here

    for t in trials:
        
        print('########## Trial {} #########'.format(trial_num))
    
        # Pupil baseline
        clock_trial.reset() # reset clock at the beginning of the trial
        stim_fix.draw() 
        win.flip()
        if eye_mode:
            eye.send_message('trial {} baseline phase 1'.format(trial_num))
        core.wait(t_baseline) 

        # Touch 1
        stim_touch.draw() 
        win.flip()
        if eye_mode:
            eye.send_message('trial {} touch1 {} phase 2'.format(trial_num, t)) 
        onset_touch1 = clock_trial.getTime()
        if touch_mode:
            solenoid_functions.send_solnenoid_pulses(t, serial_port)
        core.wait(t_touch)
        print('Touch1={}, time={}'.format(t, onset_touch1))

        respond = [] # respond, left, middle or right ('1','2','3')
        clock_rt.reset() # for latency measurements

        #Wait for response
        stim_resp.draw() 
        win.flip() 
        
        # For quitting early
        nuisance_rts1 = check_keys(clock_trial) # check if quiting or extra button pressed

        respond = event.waitKeys(maxWait = t_response, keyList=buttons, timeStamped=clock_rt, clearEvents=True)

        #Delay after response (only if responded)
        if respond:
            response, latency = respond[0]
            if eye_mode:
                eye.send_message('trial {} response {} phase 3'.format(trial_num, round(latency,2)))    
            core.wait(t_delay) # delay locked to response   
        else:
            response, latency = ('missing', np.nan)
            if eye_mode:
                eye.send_message('trial {} response {} phase 3'.format(trial_num, round(latency,2)))   
            
        print('Response={}, RT={}'.format(response, latency))

        #Touch 2 - Present feedback (second touch)
        feedback = touch2[t-1][random.randint(0,9)]
        stim_touch.draw() 
        win.flip()
        if eye_mode:
            eye.send_message('trial {} touch2 {} phase 4'.format(trial_num, feedback)) 
        onset_touch2 = clock_trial.getTime()
        if touch_mode:
            solenoid_functions.send_solnenoid_pulses(feedback, serial_port)
        core.wait(t_touch)   
        print('Touch2={}, time={}'.format(feedback, onset_touch2))
     
        # ITI
        stim_ITI.draw() 
        win.flip()
        # randomly chooses number between [] and rounds to 2 decimals
        ITI = np.round(random.uniform(t_ITI[0], t_ITI[1]), 2) # should this be between 0-3?
        if eye_mode:
            eye.send_message('trial {} ITI {} phase 5'.format(trial_num, ITI))    
        core.wait(ITI)
        print('ITI={}'.format(ITI))

        # For quitting early
        nuisance_rts2 = check_keys(clock_trial) # check if quiting or extra button pressed
        
        # correct response?
        if response == 'missing':
            correct = 0
        else:
            correct = feedback == buttons.index(response)+1 # index of buttons codes + 1 for finger 1,2,3

        # output data frame on each trial
        # ['subject','block','initial_hand','flip','trial_num','touch1','touch2','response','correct','RT','ITI','onset_trial','onset_touch1','onset_touch2', 'nuisance_rts']
        DF.loc[trial_num] = [
                subject_ID,         # subject
                int(block_counter), # block
                direction_hand,     # initial hand position
                int(flip),          # flipped (0 no, 1 yes)
                int(trial_num),     # trial number
                int(t),             # touch1
                int(feedback),      # touch2
                response,           # response
                int(correct),       # correct
                round(latency, 8),  # RT
                ITI,                # ITI
                round(onset_touch1, 4),
                round(onset_touch2, 4),
                nuisance_rts1,
                nuisance_rts2,
            ]
        DF.to_csv(output_filename)

        # add 1 on each trial to trial count
        trial_num += 1 
        
    # end of block
    # compute accuracy on this block:
    this_block = DF[DF['block']==block_counter]
    get_acc = np.mean(this_block['correct'])
    
    block_counter += 1
    print('End of block {}'.format(block_counter))
    
    return get_acc

"""
Experimental logic
"""
### START EXPERIMENT ###
# start clock
clock_rt = core.Clock()
clock_trial = core.Clock()

#### BLOCK LOOP ###
# Initial setting

# start with minimum number of unflipped blocks
for block in np.arange(MIN_BLOCKS): # 0,1,2,3,4
    get_acc = present_block()  # present blocks
    # if it is the last block from the first half...
    if block == MIN_BLOCKS - 1: # block==4
        # Show transition break depending on performance
        ### IF THEY DID NOT LEARN ###
        if get_acc < THRESH_ACC: # if they did NOT learn, then keep going with hand up
            present_break(normal_break_text)  # get ready for another unflipped block
            for block in np.arange(EXTRA_BLOCKS): # present N extra blocks 
                present_block() 
                if block < EXTRA_BLOCKS - 1: # end of experiment
                    present_break(normal_break_text)  # break after extra block
        else: # THEY LEARNED!!!!
            flip = 1  # start flipped condition
            if direction_hand == 'UPWARDS':
                direction_hand  = 'DOWNWARDS'
            else:
                direction_hand = 'UPWARDS'
            # need to dynamically update the break text by calling a function   
            first_flipped_break_text = update_break_text('first', direction_hand)
            present_break(first_flipped_break_text)
            
            for block in np.arange(FLIP_BLOCKS): # continue 
                present_block()
                if block < FLIP_BLOCKS - 1: # end of experiment
                    flipped_break_text = update_break_text('normal', direction_hand)
                    present_break(flipped_break_text)
    else:
        present_break(normal_break_text) # break first 4 blocks with initial break text
 
            
# END OF EXPERIMENT 
# close eye tracker and window
if eye_mode:
    eye.stop_recording(timestr, task)    
    
stim_instr.setText('Well done! Data transfering.....')
stim_instr.draw()
win.flip()
# close up
core.wait(3)
core.quit()

    
    




