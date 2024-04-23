#!/usr/bin/env python3

from PyDAQmx import Task
from PyDAQmx.DAQmxConstants import *
from PyDAQmx.DAQmxTypes import *
import sys
print("Python version")
print (sys.version)
print("Version info.")
print (sys.version_info)
import os
import platform
import psychopy
import threading
from rusocsci import buttonbox 
from psychopy import core, clock, visual, event, sound
import my # import my own functions

# print info
print('python version: {}'.format(platform.python_version()))
print('psychopy version: {}'.format(psychopy.__version__))
print('Using {}(with {}) for sounds'.format(sound.audioLib, sound.audioDriver))

## Setup Section
win = visual.Window([400,300], fullscr=False, monitor="testMonitor", units='cm')
mouse = event.Mouse()
# make a buttonbox
#bb = buttonbox.Buttonbox(port='com2')
bb = buttonbox.Buttonbox()

#10v=10mA
#wat is de maximale ampere, staat nu op 4mA?
Amp = 0.1 #this is your starting value
timeBetweenShock = 1.500 # 1sec
pulseTime = 0.01 #10ms per puls

Enable=visual.TextBox2(win,
                         text="Output\nEnabled",
                         color = 'black',
                         fillColor = 'lawngreen',
                         borderColor = 'forestgreen',
                         letterHeight = 0.5,
                         font='Open Sans',
                         size=(3,3),
                         pos=(-3,-1.6)
                         )
Disable=visual.TextBox2(win,
                         text="Output\nDisabled",
                         color = 'black',
                         fillColor = "coral",
                         borderColor = "darkred",
                         letterHeight = 0.5,
                         font='Open Sans',
                         size=(3,3),
                         pos=(-3,1.6)
                         )
startExp=visual.TextBox2(win,
                         text="start Experiment\nwith value:\n {}mA".format(Amp),
                         color = 'black',
                         fillColor = "gainsboro",
                         borderColor = "coral",
                         letterHeight = 0.5,
                         font='Open Sans',
                         size=(4.4,2.5),
                         pos=(1.3,-1.8)
                         )
Enable.opacity = 0.1
startExp.opacity = 0.1
Enable.autoDraw = True
startExp.autoDraw = True
Disable.autoDraw = True
win.flip()

def ask_user():
	# wait for a single button press
	while running:
		while bb.getButtons() == []:
			if not(running):
				break
		print('user stop pressed.')
		DisableDevice()

def giveShock(amplitude, time, amountPulse):
	win.flip()
	for i in range(amountPulse): 
		if outputEnable:
			try:
				AnalogOutput.WriteAnalogScalarF64(1,0,amplitude,None)
			except:
				AnalogOutput.WriteAnalogScalarF64(1,0,0,None)
			core.wait(time)
		if outputEnable:
			try:
				AnalogOutput.WriteAnalogScalarF64(1,0,-amplitude,None)
			except:
				AnalogOutput.WriteAnalogScalarF64(1,0,0,None)
			core.wait(time)
	AnalogOutput.WriteAnalogScalarF64(1,0,0.0,None)

def DisableDevice(win= win):
	global outputEnable
	global enableShocker
	global Amp
	Enable.opacity = 0.1
	Disable.opacity = 1.0
	startExp.opacity = 0.1
	print("max shock value was: {}mA".format(round(Amp,2)))
	Amp = 0.1
	enableShocker = False
	outputEnable = False
	AnalogOutput.WriteAnalogScalarF64(1,0,0.0,None)
	#win.flip()

def EnableDevice(win= win):
	global outputEnable
	Enable.opacity = 1.0
	Disable.opacity = 0.1
	startExp.opacity = 1.0
	startExp.text = "start Experiment\nwith value:\n {}mA".format(round(Amp,1))
	#win.flip()
	outputEnable = True

def StartShockSeries(win= win):
	global outputEnable
	Enable.opacity = 1.0
	Disable.opacity = 0.1
	startExp.opacity = 1.0
	startExp.fillColor = "gainsboro"
	#win.flip()
	outputEnable = True


#national instruments
numoutputs = 1
AnalogOutput = Task()
#DAQmx Configure Code
AnalogOutput.CreateAOVoltageChan("cDAQ1Mod1/ao0","",-9.0,9.0,DAQmx_Val_Volts, None)
AnalogOutput.StartTask()
AnalogOutput.WriteAnalogScalarF64(1,0,0.0,None)
running = True
thread_user = threading.Thread(target=ask_user)
thread_user.start()

enableShocker = False
giveShockTimer = clock.getTime()
#my.getCharacter(win, "start Experiment with value: {}mA".format(Amp))
 
while True:
	if mouse.isPressedIn(Enable):
		EnableDevice()
		while mouse.isPressedIn(Enable):
			continue
	
	if mouse.isPressedIn(Disable):
		DisableDevice()
		while mouse.isPressedIn(Disable):
			continue

	if mouse.isPressedIn(startExp) and outputEnable == True:
		startExp.fillColor = "coral"
		startExp.borderColor = "gainsboro"
		enableShocker = True
		win.flip()
		giveShockTimer = clock.getTime() + timeBetweenShock
		while mouse.isPressedIn(startExp):
			continue

	if giveShockTimer <= clock.getTime() and enableShocker == True:
		Amp += 0.1
		startExp.text = "shock value:\n {}mA".format(round(Amp,1))
		startExp.borderColor = "coral"
		win.flip()
		giveShockTimer = clock.getTime() + timeBetweenShock
		#core.wait(0.3)
		giveShock(Amp, pulseTime/2.0, 5)
		startExp.borderColor = "gainsboro"
		win.flip()
		
	if 'escape' in event.getKeys():
		DisableDevice()
		break

	win.flip()

running = False
AnalogOutput.StopTask()

## Closing Section
win.close()
core.quit()
