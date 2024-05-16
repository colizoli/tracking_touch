#!/usr/bin/env python
# encoding: utf-8
"""
================================================
Tracking Touch

Preprocessing pupil dilation
Python code O.Colizoli 2024 (olympia.colizoli@donders.ru.nl)
Python 3.9

Notes
-----
>> conda install matplotlib # fixed the matplotlib crashing error in 3.6
================================================
"""

############################################################################
# PUPIL ANALYSES
############################################################################
# importing python packages
import os, sys, datetime, time, shutil
import numpy as np
import pandas as pd
import preprocessing_functions_tracking_touch as pupil_preprocessing
import higher_level_functions_tracking_touch as higher
# conda install matplotlib # fixed the matplotlib crashing error in 3.6
from IPython import embed as shell # for debugging
# Need to have the EYELINK software installed on the terminal

# -----------------------
# Levels (toggle True/False)
# ----------------------- 
pre_process     = False  # pupil preprocessing is done on entire time series during the 2AFC decision task
trial_process   = False  # cut out events for each trial and calculate trial-wise baselines, baseline correct evoked responses (2AFC decision)
higher_level    = True   # all subjects' dataframe, pupil and behavior higher level analyses & figures (3AFC decision)
 
# -----------------------
# Paths
# ----------------------- 
# set path to home directory
home_dir        = os.path.dirname(os.getcwd()) # one level up from analysis folder
source_dir      = os.path.join(home_dir, 'sourcedata')
data_dir        = os.path.join(home_dir, 'derivatives')
experiment_name = 'task-touch_prediction' # 3AFC Decision Task

# copy 'sourcedata' to derivatives if it doesn't exist:
if not os.path.isdir(data_dir):
    shutil.copytree(source_dir, data_dir) 
else:
    print('Derivatives directory exists. Continuing...')

# -----------------------
# Participants
# -----------------------
ppns     = pd.read_csv(os.path.join(home_dir, 'analysis', 'participants_tracking_touch.csv'))
subjects = ['sub-{}'.format(s) for s in ppns['subject']]
    
# -----------------------
# Event-locked pupil parameters (shared)
# -----------------------
msgs                    = ['start recording', 'stop recording', 'phase 1', 'phase 2', 'phase 3', 'phase 4',]; # this will change for each task (keep phase 1 for locking to breaks)
phases                  = ['phase 2', 'phase 3', 'phase 4'] # of interest for analysis
time_locked             = ['stim_locked', 'resp_locked', 'feed_locked'] # events to consider (note: these have to match phases variable above)
baseline_window         = 0.5 # seconds before event of interest
pupil_step_lim          = [[-baseline_window, 3.0], [-baseline_window, 3.0], [-baseline_window, 3.0]] # size of pupil trial kernels in seconds with respect to first event, first element should max = 0!
sample_rate             = 1000 # Hz
break_trials            = [20, 40]  # which trial comes AFTER each break

# -----------------------
# 2AFC Decision Task, Pupil preprocessing, full time series
# -----------------------
if pre_process:
    # preprocessing-specific parameters
    tolkens = ['ESACC', 'EBLINK' ]      # check saccades and blinks based on EyeLink
    tw_blinks = 0.15                    # seconds before and after blink periods for interpolation
    mph       = 10      # detect peaks that are greater than minimum peak height
    mpd       = 1       # blinks separated by minimum number of samples
    threshold = 0       # detect peaks (valleys) that are greater (smaller) than `threshold` in relation to their immediate neighbors

    for s,subj in enumerate(subjects):
        edf = '{}_{}_recording-eyetracking_physio'.format(subj, experiment_name)

        pupilPreprocess = pupil_preprocessing.pupilPreprocess(
            subject             = subj,
            edf                 = edf,
            project_directory   = data_dir,
            eye                 = ppns['eye'][s],
            break_trials        = break_trials,
            msgs                = msgs, 
            tolkens             = tolkens,
            sample_rate         = sample_rate,
            tw_blinks           = tw_blinks,
            mph                 = mph,
            mpd                 = mpd,
            threshold           = threshold,
            )
        # pupilPreprocess.convert_edfs()              # converts EDF to asc, msg and gaze files (run locally)
        # pupilPreprocess.extract_pupil()             # read trials, and saves time locked pupil series as NPY array in processed folder
        pupilPreprocess.preprocess_pupil()          # blink interpolation, filtering, remove blinks/saccades, split blocks, percent signal change, plots output

# -----------------------
# 2AFC Decision Task, Pupil trials & mean response per event type
# -----------------------      
if trial_process:  
    # process 1 subject at a time
    for s,subj in enumerate(subjects):
        edf = '{}_{}_recording-eyetracking_physio'.format(subj, experiment_name)
        trialLevel = pupil_preprocessing.trials(
            subject             = subj,
            edf                 = edf,
            project_directory   = data_dir,
            sample_rate         = sample_rate,
            phases              = phases,
            time_locked         = time_locked,
            pupil_step_lim      = pupil_step_lim, 
            baseline_window     = baseline_window
            )
        trialLevel.event_related_subjects(pupil_dv='pupil_psc')  # psc: percent signal change, per event of interest, 1 output for all trials+subjects
        trialLevel.event_related_baseline_correction()           # per event of interest, baseline corrrects evoked responses

# -----------------------
# 2AFC Decision Task, MEAN responses and group level statistics 
# ----------------------- 
if higher_level:  
    higherLevel = higher.higherLevel(
        subjects                = subjects, 
        experiment_name         = experiment_name,
        project_directory       = data_dir, 
        sample_rate             = sample_rate,
        time_locked             = time_locked,
        pupil_step_lim          = pupil_step_lim,                
        baseline_window         = baseline_window,              
        pupil_time_of_interest  = [[0.75,1.25], [2.5,3.0]], # time windows to average phasic pupil, per event, in higher.plot_evoked_pupil
        )
    # higherLevel.higherlevel_get_phasics()       # computes phasic pupil for each subject (adds to log files)
    # higherLevel.create_subjects_dataframe()       # add baselines, concantenates all subjects, flags missed trials, saves higher level data frame
    ''' Note: the functions after this are using: task-tracking_touch.csv
    '''
    # higherLevel.average_conditions()           # group level data frames for all main effects + interaction
    # higherLevel.plot_phasic_pupil_pe()         # plots the interaction between the frequency and accuracy
    # higherLevel.plot_behavior()                # simple bar plots of accuracy and RT per mapping condition
    ## higherLevel.individual_differences()       # individual differences correlation between behavior and pupil
    
    ''' Evoked pupil response
    '''
    # higherLevel.dataframe_evoked_pupil_higher()  # per event of interest, outputs one dataframe or np.array? for all trials for all subject on pupil time series
    higherLevel.plot_evoked_pupil()              # plots evoked pupil per event of interest, group level, main effects + interaction
    
    ''' Ideal learner model
    '''
    # higherLevel.information_theory_estimates()
    # higherLevel.pupil_information_correlation_matrix()
    # higherLevel.dataframe_evoked_correlation()
    # higherLevel.plot_pupil_information_regression_evoked()
    # higherLevel.average_information_conditions()
    # higherLevel.plot_information()
    
    # not using
    # higherLevel.partial_correlation_information()
    # higherLevel.plot_information_pe()         # plots the interaction between the frequency and accuracy
    # higherLevel.information_evoked_get_phasics()
    # higherLevel.plot_information_phasics()
    # higherLevel.plot_information_phasics_accuracy_split()
    
    
    