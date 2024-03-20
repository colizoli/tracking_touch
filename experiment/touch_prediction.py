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
# from IPython import embed as shell # for Olympia debugging only, comment out if crashes

debug_mode = True #20x6 trials when False, True=6 trials
eye_mode = True

"""
PARAMETERS
"""
# Screen-specific parameters lab B.00.80A
# scnWidth, scnHeight = (1920, 1080)
scnWidth, scnHeight = (800, 600)
screen_width        = 53.5 # centimeters
screen_dist         = 58.0
grey = [128,128,128]

# response buttons
buttons = ['1', '2', '3'] # top, middle, bottom
button_names = ['top', 'middle' , 'bottom']

# Set trial conditions and randomize stimulus list
REPS = 20    # times to repeat trial unit full experiment
if debug_mode:
    reps      = 1 # debug mode reps
else:
    reps      = REPS

# Timing in seconds
t_baseline  = 0.5   # baseline pupil
t_touch     = 3
t_response  = 3
t_feedback  = 3
t_ITI       = [3.5,5.5]

# touch distributions
touch1      = [0,1,2] # top, middle, bottom
touch2      = [
    [0,0,1,1,1,1,1,1,2,2], # top
    [0,0,0,0,0,0,1,1,2,2], # middle
    [0,0,1,1,2,2,2,2,2,2] # bottom
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
    cwd = os.getcwd()
    logfile_dir = os.path.join(cwd,'raw', 'sub-{}'.format(subject_ID))
    if not os.path.isdir(logfile_dir):
        os.makedirs(logfile_dir)
    
    ## output file name with time stamp prevents any overwriting of data
    timestr = time.strftime("%Y%m%d-%H%M%S") 
    output_filename = os.path.join(logfile_dir,'sub-{}_task-touch_prediction_events_{}.csv'.format(subject_ID,timestr ))
    cols = ['subject','trial_num','touch1','touch2','response','correct','RT','ITI']
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
    \nAfter the first touch, press the Top/Middle/Bottom (1/2/3) key as fast as possible to indicate your prediction.\
    \n\nMaintain fixation on the '+' in the center of the screen for the duration of the experiment.\
    \nYou will have several breaks during which you can move your head/eyes.\
    \nBlink as you normally would.\
    \n\n<Press any button to BEGIN>"
    
    stim_instr      = visual.TextStim(win, color='black', pos=(0.0, 0.0), wrapWidth=ww) 
    stim_fix        = visual.TextStim(win, text='+',color='black', pos=(0.0, 0.0), height=fh)
    stim_touch      = visual.TextStim(win, text='Touch',color='black', pos=(0.0, 0.0), height=fh)
    stim_resp       = visual.TextStim(win, text='Response',color='black', pos=(0.0, 0.0), height=fh)
    stim_feedback   = visual.TextStim(win, text='Feedback',color='black', pos=(0.0, 0.0), height=fh)
    stim_ITI        = visual.TextStim(win, text='ITI',color='black', pos=(0.0, 0.0), height=fh)
    
    trials = touch1*reps
    np.random.shuffle(trials) # shuffle order of colors      
    print(trials)
    
    # start clock
    clock = core.Clock()
    
    ### CONFIG & CALIBRATION EYE-TRACKER ###
    if eye_mode:
        import funcs_pylink as eye
        task = 'tracking_touch_prediction'
        eye.config(subject_ID,task)
        eye.run_calibration(win, p.scnWidth, p.scnHeight)
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
            eye.send_message('trial {} new trial baseline phase 1'.format(trial_num))
        core.wait(t_baseline) 
        
        # Touch 1
        stim_touch.draw() 
        win.flip()
        if eye_mode:
            eye.send_message('trial {} touch1 {} phase 2'.format(trial_num, t)) # is this indeed touch? -Tamar
        # touch_1 = t
        core.wait(t_touch)
        print('Touch1={}'.format(t))
        
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
        if eye_mode:
            eye.send_message('trial {} response {} phase 3'.format(trial_num, round(latency,2)))    
        
        print('Response={}, RT={}'.format(response, latency))
        
        #Touch 2 - Present feedback (second touch)
        feedback = touch2[t][random.randint(0,9)]
        stim_feedback.draw() 
        win.flip()
        if eye_mode:
            eye.send_message('trial {} touch2 {} phase 4'.format(trial_num, feedback)) # is this indeed touch? -Tamar
        core.wait(t_touch)   
        print('Touch2={}'.format(feedback))
             
        # ITI
        stim_fix.draw() 
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
        correct = str(feedback) == response
        
        # output data frame on each trial --> how should this be changed? - Tamar
        # ['subject','trial_num','touch1','touch2','response','correct','RT','ITI']
        DF.loc[trial_num] = [
                int(subject_ID),    # subject
                int(trial_num),     # trial number
                int(t),             # touch1
                int(feedback),      # touch2
                response,           # response
                int(correct),       # correct
                round(latency, 8),  # RT
                ITI                 # ITI
            ]
        DF.to_csv(output_filename)
        
        trial_num += 1 
               
    # End screen for participants
    stim_instr.setText('Well done! Data transfering.....')
    stim_instr.draw()
    win.flip()
        
    # Close-up   
    if eye_mode:
        eye.stop_recording(timestr, task)
    
    core.wait(3)
    
    core.quit()


