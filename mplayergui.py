import Tkinter as tk
from Tkinter import *
from pykeyboard import PyKeyboard
import os
import time
import glob
from random import shuffle

started = 0 #0 is music not started, 1 is playing, 2 is paused

#i guess create new 'shuffled playlist' every time play is played for the first time
songlist = []
for file in os.listdir("/home/pi/Music/Resources"):
    if file.endswith(".mp3"):
        songlist.append(file)

top = tk.Tk()
top.resizable(width=False, height=False)
top.geometry('{}x{}'.format(480,320))
backPhoto = PhotoImage(file="back.png")


def createPlaylist():
	global songlist 
	shufflist = songlist
	shuffle(shufflist)
	f = open("playlist.m3u", "w")
	for i in shufflist:
		f.write("/home/pi/Music/Resources/" + i + "\n")
	f.close()
	

def backPress():
	k = PyKeyboard()
	print "back button pressed"
	k.press_keys([k.alt_key, k.tab_key])
	time.sleep(0.5)
	#k.tap_key(k.keypad_keys['Enter'])
	k.press_keys([k.shift_key, ','])
	time.sleep(0.5)
	k.press_keys([k.alt_key, k.tab_key])
    
def forwardPress():
	k = PyKeyboard()
	print "forward button pressed"
	k.press_keys([k.alt_key, k.tab_key])
	time.sleep(0.5)
	#k.tap_key(k.keypad_keys['Enter'])
	k.press_keys([k.shift_key, '.'])
	time.sleep(0.5)
	k.press_keys([k.alt_key, k.tab_key])
	
def play():
	global started
	k = PyKeyboard()
	if started == 0: #start tunes
		print "started"
		k.press_keys([k.alt_key, k.tab_key])
		time.sleep(0.5)
		k.type_string('mplayer -ao alsa:device=hw=0,0 -playlist playlist.m3u')
		k.tap_key(k.keypad_keys['Enter'])
		k.press_keys([k.alt_key, k.tab_key])
		started = 1
		createPlaylist()
	elif started == 1: #song is playing, button pauses
		print "playing"
		k.press_keys([k.alt_key, k.tab_key])
		time.sleep(0.1)
		k.tap_key('p')
		time.sleep(0.1)
		k.press_keys([k.alt_key, k.tab_key])
		
		
   

backwards = tk.Button(top, image = backPhoto, height = 70, width = 70, command = backPress)
forwards = tk.Button(top, image=backPhoto, height =70, width = 70, command = forwardPress)
play = tk.Button(top, image=backPhoto, height =70, width = 70, command = play)
backwards.place(x=70, y=140)
forwards.place(x = 320, y=140)
play.place(x = 200, y = 140)


createPlaylist()

top.mainloop()
