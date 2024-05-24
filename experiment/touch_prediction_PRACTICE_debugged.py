"""
PRACTICE Tracking touch experiment: Pupil response to prediction errors in touch
"""
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
import digitimer_functions

# TO DO: add drift correction after break!

debug_mode = True #20x6 trials when False, True=6 trials
touch_mode = True

"""
PARAMETERS
"""
hard_path = os.path.join("d:","users","Tamar", "tracking_touch-main", "experiment")
os.chdir(hard_path)

# Screen-specific parameters lab B.00.80A
scnWidth, scnHeight = (1920, 1080)
# scnWidth, scnHeight = (800, 600) # for debugging
screen_width        = 53.5 # centimeters
screen_dist         = 58.0
grey = [128,128,128]

# response buttons
buttons = ['left', 'down', 'right'] # top, middle, bottom
button_names = ['top', 'middle' , 'bottom']

# Set trial conditions and randomize stimulus list
REPS = 5    # times to repeat trial unit full experiment
if debug_mode:
    reps      = 1 # debug mode reps
else:
    reps      = REPS

# multiply intensities
int_mult = 1.2

# Timing in seconds
t_baseline  = 1   # baseline pupil
t_touch     = 1.5
t_response  = 3
t_feedback  = 1.5
t_ITI       = [3.5,5.5]

# touch distributions
touch1      = [1,2,3] # top, middle, bottom

# Size  screen 1920 x 1080, units in pixels
fh  = 50  # fixation cross height
ww = 1000 # wrap width of instructions text

"""
GET INPUT
"""
# Get subject number
g = gui.Dlg()
g.addField('Subject Number:')
g.show()
subject_ID = int(g.data[0])

if subject_ID:

     ## Create LogFile folder cwd/LogFiles
    logfile_dir = os.path.join('sourcedata', 'sub-{}'.format(subject_ID))
    if not os.path.isdir(logfile_dir):
        os.makedirs(logfile_dir)
    
    # get intensities for touch from staircase output
    staircase1 = pd.read_csv(os.path.join(logfile_dir, 'sub-{}_staircase_{}.csv'.format(subject_ID, 1)))
    staircase2 = pd.read_csv(os.path.join(logfile_dir, 'sub-{}_staircase_{}.csv'.format(subject_ID, 2)))
    staircase3 = pd.read_csv(os.path.join(logfile_dir, 'sub-{}_staircase_{}.csv'.format(subject_ID, 3)))
    
    touch_intensities = [
        np.array(staircase1['0'])[-2],    # top 
        np.array(staircase2['0'])[-2],  # middle
        np.array(staircase3['0'])[-2],  # bottom         
        ]

    touch_intensities = touch_intensities*np.array(int_mult)
        
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
    instr1_txt = "PRACTICE Touch prediction\
    \nYou will be touched on part of your finger twice in a row.\
    \nYOUR TASK IS TO PREDICT WHERE THE 2ND TOUCH WILL BE.\
    \n\nFor these practice trials, the 2nd touch will ALWAYS be on the same finger as the 1st touch!\
    \n\nAfter the first touch, press the Index/Middle/Ring finger (Left/ Down /Right) key to indicate your prediction.\
    \n\nMaintain fixation on the '+' in the center of the screen for the duration of the experiment.\
    \nBlink as you normally would, but do not move your left hand during the experiment.\
    \n\n<Press any button to CONTINUE INSTRUCTIONS>"
    
    instr2_txt = "Below is a visual example of each trial of the experiment.\
    \nGive your prediction for the finger of the 2nd touch when you see the DIAMOND symbol appear.\
    \n\nAfter the first touch, press the Index/Middle/R\ing finger (Left/ Down /Right) key as fast as possible to indicate your prediction.\
    \n\n<Press any button to BEGIN the PRACTICE TRIALS>"
    
    stim_instr1   = visual.TextStim(win, text=instr1_txt, color='black', pos=(0.0, 0.0), wrapWidth=ww)
    stim_instr2a  = visual.TextStim(win, text=instr2_txt, color='black', pos=(0.0, 100.0), wrapWidth=ww)
    stim_instr2b  = visual.ImageStim(win, image=os.path.join('stimuli', 'trial.png'), pos=(0.0, -200.0))
    
    stim_size = (40,40)
    stim_fix     = visual.ImageStim(win, image=os.path.join('stimuli', 'plus.png'), size=stim_size)
    stim_touch   = visual.ImageStim(win, image=os.path.join('stimuli', 'kruis.png'), size=stim_size)
    stim_resp    = visual.ImageStim(win, image=os.path.join('stimuli', 'ruit.png'), size=stim_size)
    stim_correct = visual.TextStim(win, text='Good job!',color='green', pos=(0.0, 0.0), height=fh)
    stim_error   = visual.TextStim(win, text='Try again...',color='red', pos=(0.0, 0.0), height=fh)
    stim_ITI     = visual.ImageStim(win, image=os.path.join('stimuli', 'plus.png'), size=stim_size)
    
    trials = touch1*reps
    np.random.shuffle(trials) # shuffle order of colors      
    print(trials)
    
    # start clock
    clock = core.Clock()
    
    # Welcome instructions
    # stim_instr1.setText(welcome_txt)
    stim_instr1.draw()
    win.flip()
    core.wait(0.25)
    event.waitKeys()
    
    stim_instr2a.draw()
    stim_instr2b.draw()
    win.flip()
    core.wait(0.25)
    event.waitKeys()
    
    # Wait a few seconds before first trial to stabilize gaze
    stim_fix.draw()
    win.flip()
    core.wait(3) 
    
    #### TRIAL LOOP ### --> add the intervals here
    trial_num = 0 # not enumerate doesn't work properly because trials has shuffled index
    for t in trials:
        
        print('########## Trial {} #########'.format(trial_num))
                    
        # Pupil baseline
        stim_fix.draw() 
        win.flip()
        core.wait(t_baseline) 
        
        # Touch 1
        t1_intensity = touch_intensities[t-1]
        stim_touch.draw() 
        win.flip()
        # touch_1 = t
        if touch_mode:
            digitimer_functions.administer_touch(this_intensity=t1_intensity, channel=t) # channels are non-zero
        core.wait(t_touch)
        print('Touch1={}, Intensity={}'.format(t, t1_intensity))
        
        respond = [] # respond, top, middle or bottom ('1','2','3')
        clock.reset() # for latency measurements
        
        #Wait for response
        stim_resp.draw() 
        win.flip() 
   
        while clock.getTime() < t_response:
            stim_resp.draw()
            win.flip()
            if not respond:
                respond = event.waitKeys(maxWait = t_response-clock.getTime() ,keyList=buttons, timeStamped=clock)
        
        if respond:
            response, latency = respond[0]
        else:
            response, latency = ('missing', np.nan)
        
        print('Response={}, RT={}'.format(response, latency))
        
        #Touch 2 - Present feedback (second touch) FOR PRACTICE ALWAYS THE SAME AS FIRST TOUCH
        feedback = t
        t2_intensity = touch_intensities[t-1]
        stim_touch.draw() 
        win.flip()
        if touch_mode:
            digitimer_functions.administer_touch(this_intensity=t2_intensity, channel=feedback) # channels are non-zero
        core.wait(t_touch)   
        print('Touch2={}, Intensity={}'.format(feedback, t2_intensity))
        
        # For quitting early
        keys = event.getKeys()
        if keys:
            # q quits the experiment
            if (keys[0] == 'q') or (keys[0] == 'escape'):
                core.quit()
        
        # correct response?
        if response == 'missing':
            correct = 0
        else:
            correct = feedback == buttons.index(response)+1 # index of buttons codes + 1 for finger 1,2,3
        
        # show feedback on accuracy for 0.5 seconds
        if correct:
            stim_correct.draw() 
        else:
            stim_error.draw() 
        win.flip()
        core.wait(1)
        
        # ITI
        # stim_fix.draw()
        stim_ITI.draw() 
        win.flip()
        # randomly chooses number between [] and rounds to 2 decimals
        ITI = np.round(random.uniform(t_ITI[0], t_ITI[1]), 2) # should this be between 0-3?
        core.wait(ITI)
        print('ITI={}'.format(ITI))
        
        trial_num += 1 
               
    # End screen for participants
    stim_instr.setText('Well done! Data transfering.....')
    stim_instr.draw()
    win.flip()
        
    # Close-up   
    core.wait(3)
    
    core.quit()


