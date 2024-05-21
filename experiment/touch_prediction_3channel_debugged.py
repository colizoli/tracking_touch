"""
Tracking touch experiment: Pupil response to prediction errors in touch
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

debug_mode = False #20x6 trials when False, True=6 trials
eye_mode = True
touch_mode = True

"""
PARAMETERS
"""
hard_path = os.path.join("d:","users","Tamar", "tracking_touch-main", "experiment")
os.chdir(hard_path)

# Screen-specific parameters lab B.00.80A
scnWidth, scnHeight = (1920, 1080)
#scnWidth, scnHeight = (800, 600) # for debugging
screen_width        = 53.5 # centimeters
screen_dist         = 58.0
grey = [128,128,128]

# response buttons
buttons = ['left', 'down', 'right'] # top, middle, bottom
button_names = ['top', 'middle' , 'bottom']

# Set trial conditions and randomize stimulus list
REPS = 60    # times to repeat trial unit full experiment
if debug_mode:
    reps      = 1 # debug mode reps
else:
    reps      = REPS

break_trials = [20,40,60,80,100,120,140,160]

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
touch2      = [
    [1,1,2,2,2,2,2,2,3,3], # top
    [1,1,1,1,1,1,2,2,3,3], # middle
    [1,1,2,2,3,3,3,3,3,3]  # bottom
           ]

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
    logfile_dir = os.path.join( 'sourcedata', 'sub-{}'.format(subject_ID))
    if not os.path.isdir(logfile_dir):
        os.makedirs(logfile_dir)
    
    # get intensities for touch from staircase output
    staircase1 = pd.read_csv(os.path.join(logfile_dir, 'sub-{}_staircase_{}.csv'.format(subject_ID, 1)))
    staircase2 = pd.read_csv(os.path.join(logfile_dir, 'sub-{}_staircase_{}.csv'.format(subject_ID, 2)))
    staircase3 = pd.read_csv(os.path.join(logfile_dir, 'sub-{}_staircase_{}.csv'.format(subject_ID, 3)))
    
    touch_intensities = [
        np.array(staircase1['0'])[-2],  # top 
        np.array(staircase2['0'])[-2],  # middle
        np.array(staircase3['0'])[-2],  # bottom         
        ]
    
    touch_intensities = touch_intensities*np.array(int_mult)
        
    ## output file name with time stamp prevents any overwriting of data
    timestr = time.strftime("%Y%m%d-%H%M%S") 
    output_filename = os.path.join(logfile_dir,'sub-{}_task-touch_prediction_events_{}.csv'.format(subject_ID,timestr ))
    cols = ['subject','trial_num','touch1','touch2','response','correct','RT','ITI','t1_intensity','t2_intensity']
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
    welcome_txt = "Touch prediction\
    \nYou will be touched on part of your finger twice in a row.\
    \nYour task is to predict where the 2nd touch will be.\
    \nAfter the first touch, press the Index/Middle/Ring finger (Left/ Down /Right) key as fast as possible to indicate your prediction.\
    \n\nMaintain fixation on the '+' in the center of the screen for the duration of the experiment.\
    \nYou will have several breaks during which you can move your head/eyes.\
    \nBlink as you normally would.\
    \n\n<Press any button to BEGIN>"
    
    stim_size = (40,40)
    stim_fix        = visual.ImageStim(win, image=os.path.join('stimuli', 'plus.png'), size=stim_size)
    stim_touch      = visual.ImageStim(win, image=os.path.join('stimuli', 'kruis.png'), size=stim_size)
    stim_resp       = visual.ImageStim(win, image=os.path.join('stimuli', 'ruit.png'), size=stim_size)
    stim_ITI        = visual.ImageStim(win, image=os.path.join('stimuli', 'plus.png'), size=stim_size)
    stim_instr      = visual.TextStim(win, color='black', pos=(0.0, 0.0), wrapWidth=ww)

    stim_instr      = visual.TextStim(win, color='black', pos=(0.0, 0.0), wrapWidth=ww) 
    #stim_fix        = visual.TextStim(win, text='+',color='black', pos=(0.0, 0.0), height=fh)
    #stim_touch      = visual.TextStim(win, text='Touch',color='black', pos=(0.0, 0.0), height=fh)
    #stim_resp       = visual.TextStim(win, text='Response',color='black', pos=(0.0, 0.0), height=fh)
    #stim_feedback   = visual.TextStim(win, text='Feedback',color='black', pos=(0.0, 0.0), height=fh)
    #stim_ITI        = visual.TextStim(win, text='ITI',color='black', pos=(0.0, 0.0), height=fh)
    
    trials = touch1*reps
    np.random.shuffle(trials) # shuffle order of colors      
    print(trials)
    
    # start clock
    clock = core.Clock()
    
    ### CONFIG & CALIBRATION EYE-TRACKER ###
    if eye_mode:
        import funcs_pylink3 as eye
        task = 'tracking_touch_prediction'
        eye.config(subject_ID,task)
        eye.run_calibration(win, scnWidth, scnHeight)
        eye.start_recording()
        eye.send_message('subject_ID sub-{} task-{} timestamp {}'.format(subject_ID, task ,timestr))
    
    # Welcome instructions
    stim_instr.setText(welcome_txt)
    stim_instr.draw()
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
        if eye_mode:
            eye.send_message('trial {} baseline phase 1'.format(trial_num))
        core.wait(t_baseline) 
        
        # Touch 1
        t1_intensity = touch_intensities[t-1]
        stim_touch.draw() 
        win.flip()
        if eye_mode:
            eye.send_message('trial {} touch1 {} phase 2'.format(trial_num, t)) # is this indeed touch? -Tamar
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
                respond = event.waitKeys(maxWait = t_response-clock.getTime(), keyList=buttons, timeStamped=clock)
        
        if respond:
            response, latency = respond[0]
        else:
            response, latency = ('missing', np.nan)
        if eye_mode:
            eye.send_message('trial {} response {} phase 3'.format(trial_num, round(latency,2)))    
        
        print('Response={}, RT={}'.format(response, latency))
        
        #Touch 2 - Present feedback (second touch)
        feedback = touch2[t-1][random.randint(0,9)]
        t2_intensity = touch_intensities[feedback-1]
        stim_touch.draw() 
        win.flip()
        if eye_mode:
            eye.send_message('trial {} touch2 {} phase 4'.format(trial_num, feedback)) # is this indeed touch? -Tamar
        if touch_mode:
            digitimer_functions.administer_touch(this_intensity=t2_intensity, channel=feedback) # channels are non-zero
        core.wait(t_touch)   
        print('Touch2={}, Intensity={}'.format(feedback, t2_intensity))
             
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
        keys = event.getKeys()
        if keys:
            # q quits the experiment
            if (keys[0] == 'q') or (keys[0] == 'escape'):
                if eye_mode:
                    eye.stop_skip_save()
                core.quit()
        
        # correct response?
        if response == 'missing':
            correct = 0
        else:
            correct = feedback == buttons.index(response)+1 # index of buttons codes + 1 for finger 1,2,3
        
        # output data frame on each trial --> how should this be changed? - Tamar
        # ['subject','trial_num','touch1','touch2','response','correct','RT','ITI','t1_intensity','t2_intensity']
        DF.loc[trial_num] = [
                int(subject_ID),    # subject
                int(trial_num),     # trial number
                int(t),             # touch1
                int(feedback),      # touch2
                response,           # response
                int(correct),       # correct
                round(latency, 8),  # RT
                ITI,                 # ITI
                round(t1_intensity, 8),  # touch 1 intensity
                round(t2_intensity, 8),  # touch 2 intensity
            ]
        DF.to_csv(output_filename)
        
        trial_num += 1 
        
        # break!!
        if trial_num in break_trials:
            
            if eye_mode:
                eye.pause_stop_recording() # pause recording
            
            # Break instructions forced 
            stim_instr.setText('Take a short break!')
            stim_instr.draw()
            win.flip()
            core.wait(0.5)
            
            # Break instructions continue
            stim_instr.setText('Take a short break! \n\n Push a button when you are ready to continue.')
            stim_instr.draw()
            win.flip()
            event.waitKeys()
            
            if eye_mode:
                # Drift correction, when subject moves their head during breaks
                eye.run_drift_correction(win, scnWidth, scnHeight)
               
    # End screen for participants
    stim_instr.setText('Well done! Data transfering.....')
    stim_instr.draw()
    win.flip()
        
    # Close-up   
    if eye_mode:
        eye.stop_recording(timestr, task)
    
    core.wait(3)
    
    core.quit()


