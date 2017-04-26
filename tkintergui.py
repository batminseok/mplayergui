import Tkinter as tk   # python
from Tkinter import *
from pykeyboard import PyKeyboard
import os
import subprocess
import time
import glob
from random import shuffle
from PIL import ImageTk
from PIL import Image
import mutagen
from mutagen.mp3 import *
from mutagen.id3 import ID3

TITLE_FONT = ("Helvetica", 18, "bold")

#subprocess.Popen("amixer set Digital 50%", shell = True) volume eventually 

started = 0 #for keeping track of start or not
songNumber = 0 #for keeping track of place in playlist

songlist = []

for file in os.listdir("/home/pi/Music/Resources"):
    if file.endswith(".mp3"):
        songlist.append(file)
        

        
def createPlaylist():
	global songlist 
	shufflist = songlist
	shuffle(shufflist)
	f = open("playlist.m3u", "w")
	for i in shufflist:
		f.write("/home/pi/Music/Resources/" + i + "\n")
	f.close()
	

def getSong(): #which song is currently being played
	global songNumber
	with open("playlist.m3u") as fp:
		for i, line in enumerate(fp):
			if i == songNumber:
				currentSong = line
				print "current song(get song): " + str(i) 
	formattedSong = currentSong.rstrip()
	formattedSong = formattedSong.replace('.mp3', '')
	formattedSong = formattedSong.replace('/home/pi/Music/Resources/', '')
	print formattedSong
	return formattedSong
	
	

class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        self.resizable(width=False, height=False)
        self.geometry('{}x{}'.format(480,320))
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        

        self.frames = {}
        for F in (nowPlaying, songList):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("nowPlaying")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class nowPlaying(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.switchbutton = tk.Button(self, height = 100, width = 100,
                            command=lambda: controller.show_frame("songList"))
        self.switchbutton.place(relx=0.5, rely=0.20, anchor= CENTER)
        
        w = Label(self, text = "Song Title")
        
        backwards = tk.Button(self, height = 4, width = 5, command = self.backPress)
        backwards.place(relx=0.26, rely=0.8, anchor= CENTER)
        
        play = tk.Button(self, height = 4, width = 5, command = self.playPress)
        play.place(relx=0.5, rely=0.8, anchor= CENTER)
        
        forwards = tk.Button(self, height = 4, width = 5, command = self.forwardPress)
        forwards.place(relx=0.74, rely=0.8, anchor= CENTER)
        
    def backPress(self):
		
		k = PyKeyboard()
		
		if started == 1:
			print "back button pressed"
			k.press_keys([k.alt_key, k.tab_key])
			time.sleep(0.5)
			k.press_keys([k.shift_key, ','])
			time.sleep(0.5)
			k.press_keys([k.alt_key, k.tab_key])
			
			global songNumber
			songNumber -= 1
			
			print "global: " + str(songNumber)
			song = getSong()
			pngstring = "/home/pi/Music/Albumart/" + song + ".png"
			try:
				photo2 = ImageTk.PhotoImage(file = pngstring)
				self.switchbutton.config(image = photo2)
				self.switchbutton.image = photo2
			except:
				print "srry"
		
		
    def playPress(self):
		
		global started
		global songNumber
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
			
			song = getSong()
			pngstring = "/home/pi/Music/Albumart/" + song + ".png"
			try:
				photo2 = ImageTk.PhotoImage(file = pngstring)
				self.switchbutton.config(image = photo2)
				self.switchbutton.image = photo2
			except:
				print "srry"
			print "global: " + str(songNumber)
			
		elif started == 1: #song is playing, button pauses
			print "playing"
			k.press_keys([k.alt_key, k.tab_key])
			time.sleep(0.1)
			k.tap_key('p')
			time.sleep(0.1)
			k.press_keys([k.alt_key, k.tab_key])
		
		
    def forwardPress(self):
		
		if started == 1:
			global songNumber
			songNumber += 1
			
			song = getSong()
			pngstring = "/home/pi/Music/Albumart/" + song + ".png"
			try:
				photo2 = ImageTk.PhotoImage(file = pngstring)
				self.switchbutton.config(image = photo2)
				self.switchbutton.image = photo2
			except:
				print "srry"
			
			k = PyKeyboard()
			print "forward button pressed"
			k.press_keys([k.alt_key, k.tab_key])
			time.sleep(0.5)
			k.press_keys([k.shift_key, '.'])
			time.sleep(0.5)
			k.press_keys([k.alt_key, k.tab_key])
			
		


class songList(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        button = tk.Button(self, text="back",
                           command=lambda: controller.show_frame("nowPlaying"))
        button.pack()



if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
