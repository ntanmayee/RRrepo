'''
RRA Player v0.8
Revision Date: 17th June 2013

Utilities:
	- 'Now Playing' label
	- Play / Pause
	- File Browser
	- Volume Control
	- Scrubber

Authors: Tanmayee Narendra , Yashvanth Kondi

Operation: Select desired RRA file using "Open" button. Click Play/Replay Button in order to
start playing the file. Click Pause/Unpause button to pause/unpause the song. Adjust volume
by dragging the volume slider on the side up/down (default value is 100 => 100% of original volume).
Adjust position of where the song is played from using SEEK scrubber (resolution: blocks of 0.1%
of song length). Upon completion of playing a clip, if another clip is to be played, repeat the
above procedure. To close the program, close the Tkinter GUI window and use CTRL+C and CTRL+Z
for good measure, to kill all processes.

WARNING: Unstable on completion of playing all audio clips. KeyboardInterrupt (CTRL+C and CTRL+Z)
must be used upon exiting GUI in order to terminate the arplay1 thread. In some cases, the ALSA
device continues to be blocked even after all program processes have been killed (marked by the 
lack of audio playback from any source). In these cases, the terminal must be closed and started again.
Upon clicking the Play/Replay button for the first time during an instance of execution, in
some cases where an audio file of any sort was recently played, ALSA may throw a "Device Busy"
error. In these cases, repeat clicking the Play button until the file plays. If the problem persists
after 3-4 attempts, it is suggested that this program be closed altogether and restarted.

'''
from Tkinter import *
import time
from os import system, path
import os.path
from tkFileDialog import askopenfilename
import threading
import time
import tkFont

filepath = ''
playNow = 0
volume = 0
scrub = 0
playFlag = 0
playing = None


def play():
	if filepath == '':
		return 
	details = path.split(filepath) 
	system('cd '+details[0])
	system('./arplay1 '+details[1])
	print 'Done playing', details[1]

def player():
	global playNow
	global volume
	global scrub
	infile = open(path.split(filepath)[1], 'r')
	outfile = open('~tempRRA', 'a')
	flag = 0
	last = '0\n'
	counter = 0
	x = 0
	pos = 0
	secondspersample = 0.86/44000
	filesize = os.path.getsize(path.split(filepath)[1])
	block = filesize / 1000.0
	while True:
		i = infile.readline()
		if not i:
			break
		if flag == 1:
			sample = int(i)*(x/100.0)
			outfile.write(str(int(sample)) + '\n')
			while playNow % 2 == 1:
				flag = 1
			counter = counter + 1
			start = time.time()
			while time.time() - start < secondspersample:
				if counter > 1000:
					x = volume.get()
					pos = scrub.get()
					if abs(pos - infile.tell()/block) >10:
						infile.seek(block * pos , 0)
						sampleBuffer = infile.readline()
						sampleBuffer = infile.readline()
					scrub.set( int(infile.tell() / block) )
					counter = 0
		else:
			if i == '%%\n':
				flag = 1
			outfile.write(last)
	print 'done playing'

def playRRA():
	global playFlag
	if playFlag == 0:
		temp = open('~tempRRA', 'w')
		temp.close()
		playThread = threading.Thread(target = play)
		playThread.start()
	#scrub.set(60)
	playerThread = threading.Thread(target = player)
	playerThread.start()
	playFlag = 1
   
def pauseRRA():
	global playNow
	playNow = playNow + 1

def rootName(filename):
	pos = 0
	while filename[pos] != '.':
		pos = pos + 1
	return filename[:pos]

def openRRA():
	global filepath
	filepath = askopenfilename(filetypes=[("RRA Files","*.rra"),])
	playing.set("Now Playing: "+rootName(path.split(filepath)[1]))
	scrub.set(0)
   
def windowSetup():
	top = Tk()
	global filepath
	global playNow
	global volume
	global scrub
	global playing
	playing = StringVar()
	playing.set("Now Playing: ")
	top.configure(background='black')
	filepath = None
	playNow = 0
	top.geometry('390x100')
	top.title('RRA Player v0.8 Alpha')
	frameWork = Frame(top)
	volume = Scale(top, from_=200, to=0, label = "Volume", bg = 'black', fg = 'white')
	volume.pack(side=RIGHT)
	volume.set(100)
	scrub = Scale(top, from_=0, to=1000, length = 250, orient = HORIZONTAL, label = "_________________SEEK_________________", bg = 'blue', relief = RIDGE, showvalue = 0, sliderlength = 15, highlightbackground = 'white', highlightcolor = 'white', fg = 'white', cursor = 'target')
	scrub.pack(side=TOP)
	scrub.set(0)
	Label(top, textvariable = playing).pack()
	play = Button(frameWork, text = 'Play / Replay', command = playRRA, bg = 'red')
	play.pack(side=LEFT)
	stop = Button(frameWork, text = 'Pause / Unpause', command = pauseRRA, bg = 'darkgreen', fg = 'white')
	stop.pack(side=LEFT)
	openFile = Button(top, text = 'Open', command = openRRA, bg = 'black', fg = 'white', cursor = 'plus')
	openFile.pack(side = RIGHT)
	frameWork.pack(side = BOTTOM)
	top.mainloop()

if __name__ == '__main__':
	try:
		windowSetup()
	except (KeyboardInterrupt, SystemExit):
		system('rm ~tempRRA')
		sys.exit(0)
