import Tkinter as tk   # python
from Tkinter import *
import ttk
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

#subprocess.Popen("amixer set Digital 50%", shell = True) volume eventually 

started = 0 #for keeping track of start or not
songNumber = 0 #for keeping track of place in playlist
paused = 0

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
	formattedSong = currentSong.rstrip().replace('.mp3', '').replace('/home/pi/Music/Resources/', '')
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
        self.configure(background = 'white')
        #self.overrideredirect(1) #for getting rid of bar eventually
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
        frame = tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.configure(background = 'white')

        self.switchbutton = tk.Button(self, height = 100, width = 100, highlightthickness = 0, bd = 0, bg = 'white',
                            activebackground = 'white', relief = SUNKEN, command=lambda: controller.show_frame("songList"))
        self.switchbutton.place(relx=0.5, rely=0.20, anchor= CENTER)
        
        self.songTitle = Label(self, text = "Song Title", bg = 'white', font = ('Andale Mono', 10,"bold"), fg = 'gray27')
        self.songTitle.place(relx = 0.5, rely = 0.4, anchor = CENTER)
        
        self.artistName = Label(self, text = "Artist Name", bg = 'white', font = ('Andale Mono', 10), fg = 'gray27')
        self.artistName.place(relx = 0.5, rely = 0.46, anchor = CENTER)
        
        backwards = tk.Button(self, height = 4, width = 5, command = self.backPress)
        backwards.place(relx=0.26, rely=0.8, anchor= CENTER)
        
        play = tk.Button(self, height = 4, width = 5, command = self.playPress)
        play.place(relx=0.5, rely=0.8, anchor= CENTER)
        
        forwards = tk.Button(self, height = 4, width = 5, command = self.forwardPress)
        forwards.place(relx=0.74, rely=0.8, anchor= CENTER)
        
        s = ttk.Style()
        s.theme_use('alt')
        s.configure("TProgressbar", foreground = 'white', background = 'white', troughcolor = 'gray27', thickness = 5,)
        self.progressBar = ttk.Progressbar(self, style = "TProgressbar", orient = "horizontal", 
		                       length = 420, mode = "determinate", maximum = 100)
        self.progressBar.place(relx = 0.5, rely = 0.55, anchor = CENTER)
        
        self.secv = StringVar()
        self.seconds = 0
        
        self.secondslabel = Label(self, textvariable = self.secv)
        self.place(relx = 0.5, rely = 0.6, anchor = CENTER)
		
        
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
			self.progressBar.stop()
			self.after_cancel(self.songtimer)
			print "cancelled timer"
			self.editInfo()
		
		
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
			
			createPlaylist()
			
			self.editInfo() #runs main looping through music loop
			
			started = 1
			
		elif started == 1: #song is playing, button pauses
			global paused
			print "playing"
			k.press_keys([k.alt_key, k.tab_key])
			time.sleep(0.1)
			k.tap_key('p')
			time.sleep(0.1)
			k.press_keys([k.alt_key, k.tab_key])
			#got to get timestamp...... somehow
			#seperate after timer? to count maybe
			#then once you get time, stop progressbar
			#do some magic to find out postion you want step to be in then step song + restart timer
			#then create new after for the rest 
			#need play/pause bit
			if paused == 0: #if playing
				#change icon
				#cancel after_timer 
				#pause progress bar
				#store current time somewhere
				self.after_cancel(self.pause)
				print "paused"
				paused = 1
			elif paused == 1: #if paused
				#change icon
				#get time through song 
				#restart progress bar at delta, do some maths for that 
				#create new timer using similar to IncreasesongNumber
				#when timer hits length, increase song number
				self.timer()
				print "played"
				paused = 0
				
		
    def forwardPress(self):
		
		if started == 1:
			global songNumber
			songNumber += 1
			
			k = PyKeyboard()
			print "forward button pressed"
			k.press_keys([k.alt_key, k.tab_key])
			time.sleep(0.5)
			k.press_keys([k.shift_key, '.'])
			time.sleep(0.5)
			k.press_keys([k.alt_key, k.tab_key])
			self.progressBar.stop()
			#ok so here we want to cancel the previous increaseSongNumber
			self.after_cancel(self.songtimer)
			self.after_cancel(self.pause)
			print "cancelled timer"
			self.editInfo()
			
			
				
    def editInfo(self):
		print "info edited"
		global started
		song = getSong()# #get song name eg Just.mp3
		pngstring = "/home/pi/Music/Albumart/" + song + ".png"
		mp3string = "/home/pi/Music/Resources/" + song + ".mp3"
		mp3 = MP3(mp3string)
		intervalLength = int(mp3.info.length) * 10 #bars' currently a bit out
		if started == 0:
			self.length = int(mp3.info.length * 1000) + 2000 #add a few second delay for first song for mplayer init>
			print "added extra time for start"
		else: 
			self.length = int(mp3.info.length * 1000) 
		print self.length
		title = mp3["TIT2"]
		artist = mp3["TPE1"]
		self.artistName.config(text = artist)
		self.songTitle.config(text = title)
		try:
			photo2 = ImageTk.PhotoImage(file = pngstring)
			self.switchbutton.config(image = photo2)
			self.switchbutton.image = photo2
		except:
			print "srry"
			#could put placeholder image here/or just sort art out tbh
		self.progressBar.start(intervalLength)
		global songNumber
		self.songtimer = self.after(self.length, self.increaseSongNumber) #ok so this works for just looping through songs
		self.seconds = 0
		self.timer() #add in time left variable?
		print "after started"
		
    def increaseSongNumber(self): #getting done 4x
		global songNumber #could replace these globals with selfs
		songNumber += 1
		print songNumber
		print "increased song number"
		self.progressBar.stop()
		self.editInfo()
			
    def timer(self): #count up 
		print "triggered"
		self.secv.set(self.seconds) #make sure this is all placed right/seconds are good
		print self.seconds
		self.seconds += 1
		print self.length / 1000
		    self.pause = self.after(1000, self.timer) 
		
			
		
		


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
