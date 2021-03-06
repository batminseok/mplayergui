#!/usr/bin/env python

import Tkinter as tk   
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
import thread


started = 0 #for keeping track of start or not
songNumber = 0 #for keeping track of place in playlist
selected = 0
volume = 7
paused = False

volumeList = [0, 15, 40, 60, 75, 85, 95, 105, 110, 118, 120, 122, 128, 133, 137, 140, 
                145, 148, 151, 154, 157, 159, 162]
                
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
    
def callmplayer():#really fuck
    thread.start_new_thread(dumbworkaround, ())
    
def dumbworkaround():
	os.system('mplayer -slave -ao alsa:device=hw=0,0 -playlist playlist.m3u')


def onselect(evt):
	print "hi!"
	#kill mplayer 
	#remake playlist with song x at the beginning
	#start playing 
	#invoke play button?
	w = evt.widget
	index = int(w.curselection()[0])
	value = w.get(index) + ".mp3" #song value
	print value
	global songlist
	songlist.remove(value)
	shufflist = songlist
	shuffle(shufflist)
	shufflist.insert(0, value)
	print shufflist  
	f = open("playlist.m3u", "w")
	for i in shufflist:
		f.write("/home/pi/Music/Resources/" + i + "\n")
	f.close() #up to here works perfectly
	global started
	global selected
	started = 0 #playlist hasnt started
	selected = 1 #song has been selected
    
	
class mp3App(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.resizable(width=False, height=False) 
        self.geometry('{}x{}'.format(480,320))
        self.configure(background = 'white')
        self.overrideredirect(1) #for getting rid of bar eventually
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        

        self.frames = {}
        for F in (nowPlaying, songList, sleepBox, optionsBox):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("nowPlaying")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class nowPlaying(tk.Frame):

    def __init__(self, parent, controller):
        frame = tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.seconds = 0
        self.config(cursor = "none") #for getting rid of mouse eventually also
        
        self.playphoto = ImageTk.PhotoImage(file = "/home/pi/Music/play_button.png")
        self.pausebutton = ImageTk.PhotoImage(file = "/home/pi/Music/pause_button.png")
        self.missingartwork = ImageTk.PhotoImage(file = "/home/pi/Music/missing_artwork.png")
        forwardphoto = ImageTk.PhotoImage(file = "/home/pi/Music/forwardarrow.png")
        backwardphoto = ImageTk.PhotoImage(file = "/home/pi/Music/backarrow.png")
        volupphoto = ImageTk.PhotoImage(file = "/home/pi/Music/plus.png")
        voldownphoto = ImageTk.PhotoImage(file = "/home/pi/Music/minus.png")
        
        self.secv = StringVar()
        self.minv = StringVar()
        self.lengthv = StringVar()
        
        self.configure(background = 'white')
        
        self.sleepbutton = tk.Button(self, text="sleep", width = 5, height = 3, bg = '#A2D5AC', activebackground = '#A2D5AC', 
                               highlightthickness = 0, bd = 0, fg = 'white', activeforeground = 'white', font = ('Andale Mono', 10,"bold"), command=lambda: controller.show_frame("sleepBox"))
        self.sleepbutton.place(relx = 0.2, rely = 0.24, anchor = CENTER)
        
        
        optionsButton = tk.Button(self, text="options", width = 5, height = 3, bg = '#A2D5AC', activebackground = '#A2D5AC', 
                               highlightthickness = 0, bd = 0, fg = 'white', activeforeground = 'white', font = ('Andale Mono', 10,"bold"),
                           command=lambda: controller.show_frame("optionsBox"))
        optionsButton.place(relx = 0.8, rely = 0.24, anchor = CENTER)

        self.switchbutton = tk.Button(self, height = 130, width = 130, highlightthickness = 0, bd = 0, bg = 'white',
                            activebackground = 'white', relief = SUNKEN, command=lambda: controller.show_frame("songList"))
        self.switchbutton.place(relx=0.5, rely=0.24, anchor= CENTER)
        self.switchbutton.config(image = self.missingartwork)
        self.switchbutton.image = self.missingartwork
        
        self.songTitle = Label(self, text = "Song Title", bg = 'white', font = ('Andale Mono', 10,"bold"), fg = 'gray27')
        self.songTitle.place(relx = 0.5, rely = 0.50, anchor = CENTER)
        
        self.artistName = Label(self, text = "Artist Name", bg = 'white', font = ('Andale Mono', 10), fg = 'gray27')
        self.artistName.place(relx = 0.5, rely = 0.56, anchor = CENTER)
        
        s = ttk.Style()
        s.theme_use('alt')
        s.configure("TProgressbar", foreground = '#A2D5AC', background = '#A2D5AC', troughcolor = 'white', thickness = 5, relief = RAISED, bd = 0, highlightthickness = 0, highlightcolor = 'white')
        self.progressBar = ttk.Progressbar(self, style = "TProgressbar", orient = "horizontal", 
                               length = 350, mode = "determinate", maximum = 100)
        self.progressBar.place(relx = 0.5, rely = 0.64, anchor = CENTER)
        self.progressBar.focus()
        
        self.timerLabel = Label(self, textvariable = self.secv, bg = 'white', font = ('Andale Mono', 10), fg = 'gray27')
        self.timerLabel.place(relx = 0.09, rely = 0.64, anchor = CENTER)
        
        self.lengthLabel = Label(self, textvariable = self.lengthv, bg = 'white', font = ('Andale Mono', 10), fg = 'gray27')
        self.lengthLabel.place(relx = 0.91, rely = 0.64, anchor = CENTER)
        
        backwards = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.backPress)
        backwards.place(relx=0.35, rely=0.81, anchor= CENTER)
        backwards.config(image = backwardphoto)
        backwards.image = backwardphoto
        
        self.play = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.playPress)
        self.play.place(relx=0.5, rely=0.81, anchor= CENTER)
        self.play.config(image = self.playphoto)
        self.play.image = self.playphoto
        
        forwards = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.forwardPress)
        forwards.place(relx=0.65, rely=0.81, anchor= CENTER)
        forwards.config(image = forwardphoto)
        forwards.image = forwardphoto
        
        volumeUp = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.volumeUpPress)
        volumeUp.place(relx = 0.8, rely = 0.81, anchor = CENTER)
        volumeUp.config(image = volupphoto)
        volumeUp.image = volupphoto
        
        volumeDown = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.volumeDownPress)
        volumeDown.place(relx = 0.20, rely = 0.81, anchor = CENTER)
        volumeDown.config(image = voldownphoto)
        volumeDown.image = voldownphoto
        
        
        
        
        
        
    def backPress(self):
        
        k = PyKeyboard()
        
        if started == 1:
            print "back button pressed"
            os.system("bash /home/pi/Music/mplayerbash.sh key_down_event 60")
            
            self.progressBar.stop()
            self.after_cancel(self.count)
            self.decreaseSongNumber()
            self.secv.set('0:00')
        
    def playPress(self):
        
        global started
        global songNumber 
        global selected
        k = PyKeyboard()
        print "started = " + str(started)
        global paused
        
        if started == 0: #start tunes
			
			#ok so if a new song has been selected 
			#playlist is already created
			#kill mplayer
			#set songnumber too 
			os.system("sudo killall -v mplayer")
			if selected == 0:
				createPlaylist()
			else:
				songNumber = 0
				#reset progress bar
				self.progressBar.stop()
				paused = False
				selected = 0
			self.play.config(image = self.pausebutton)
			self.play.image = self.pausebutton
			callmplayer()
			os.system("amixer set Digital 100")
			self.editInfo() #runs main looping through music loop
			started = 1
            
        elif started == 1: #song is playing, button pauses
            global paused
            print "playing"
            
            if paused == False: #if playing
                os.system("bash /home/pi/Music/mplayerbash.sh key_down_event 112")
                print "bash called"
                
                pausebutton = ImageTk.PhotoImage(file = "/home/pi/Music/play_button.png")
                self.play.config(image = pausebutton)
                self.play.image = pausebutton
                self.after_cancel(self.count)
                step_amount = ((1 - (self.seconds / self.length)) * 100)
                print str(step_amount)
                self.progressBar.stop()
                print "paused"
                self.progressBar.step(step_amount) #step is a %
                paused = True
            else:
                os.system("bash /home/pi/Music/mplayerbash.sh key_down_event 112")
                print "bash called"
                pausebutton = ImageTk.PhotoImage(file = "/home/pi/Music/pause_button.png")
                self.play.config(image = pausebutton)
                self.play.image = pausebutton
                self.timer()
                self.progressBar.start(self.intervalLength)
                print "playing"
                paused = False
                
        
    def forwardPress(self):
        
        if started == 1:
            
            k = PyKeyboard()
            print "forward button pressed"
            os.system("bash /home/pi/Music/mplayerbash.sh key_down_event 62")
            self.progressBar.stop()
            self.after_cancel(self.count)
            self.increaseSongNumber()
            self.secv.set('0:00')
            
            
                
    def editInfo(self):
        print "info edited"
        global started
        global paused
        
        song = getSong()# #get song name eg Just.mp3
        pngstring = "/home/pi/Music/Albumart/" + song + ".png"
        mp3string = "/home/pi/Music/Resources/" + song + ".mp3"
        mp3 = MP3(mp3string)
        
        self.length = mp3.info.length
        
        self.intervalLength = int(self.length) * 10 #bars' currently a bit out
        
        title = mp3["TIT2"]
        artist = mp3["TPE1"]
        self.artistName.config(text = artist)
        self.songTitle.config(text = title)
        self.seconds = self.length
        seconds = int(self.length%60)
        minutes = int(self.length/60)
        if seconds < 10:
            self.lengthv.set(str(minutes) + ':0' + str(seconds))
        else:
            self.lengthv.set(str(minutes) + ':' + str(seconds))
        
        if started == 0:
            self.seconds += 1
        print self.seconds
        
        try:
            photo2 = ImageTk.PhotoImage(file = pngstring)
            self.switchbutton.config(image = photo2)
            self.switchbutton.image = photo2
        except:
            print "srry"
            self.switchbutton.config(image = self.missingartwork)
            self.switchbutton.image = self.missingartwork
            
        try:
            self.after_cancel(self.count)
        except:
            print "caught"
        
        #if not paused, used to not start timer on skip events + avoid double timer: 
        if paused == False:
            self.timer()
            self.progressBar.start(self.intervalLength)
        
        print "after started"
        
        
        
    def timer(self): #could be nice to display on the bar or something
        
        seconds = int((self.length - self.seconds)%60)
        minutes = int((self.length - self.seconds)/60)
        if seconds < 10:
            self.secv.set(str(minutes) + ':0' + str(seconds))
        else:
            self.secv.set(str(minutes) + ':' + str(seconds))
            
            
        self.seconds -= 1
        if self.seconds < 1:
            print "timer finished"
            self.increaseSongNumber()
        else:
            self.count = self.after(1000, self.timer)
        
        
    def increaseSongNumber(self):
        global songNumber
        self.after_cancel(self.count)
        songNumber += 1
        print "song number = " + str(songNumber)
        self.editInfo()
        
        
    def decreaseSongNumber(self):
        global songNumber
        self.after_cancel(self.count)
        songNumber -= 1
        print "song number (decreased)= " + str(songNumber)
        self.editInfo()
        
        
    def volumeUpPress(self):
		global volume
		global volumeList
		if volume < len(volumeList):
		    volume += 1
		#else if volume > len(volumeList):
		#	
		setVolume = volumeList[volume]
		print setVolume
		volstring = "amixer set Digital " + str(setVolume)
		os.system(volstring)
        
    def volumeDownPress(self):
		global volume
		if volume > 0:
		    volume -= 1
		global volumeList
		setVolume = volumeList[volume]
		print setVolume
		volstring = "amixer set Digital " + str(setVolume)
		os.system(volstring)
   	
        
        


class songList(tk.Frame): #should have another frame for 'turning off' the screen

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.configure(background = 'white')
        
        backButton = tk.Button(self, text="back", width = 100, height = 3, bg = '#A2D5AC', activebackground = '#A2D5AC', 
                               highlightthickness = 0, bd = 0, fg = 'white', activeforeground = 'white', font = ('Andale Mono', 10,"bold"),
                           command=lambda: controller.show_frame("nowPlaying"))
        backButton.pack()
        
        
        scrollBar = Scrollbar(self, bg = '#A2D5AC', troughcolor = 'white', bd = 0, width = 50, relief = FLAT, activebackground = '#A2D5AC')
        scrollBar.pack(side=RIGHT, fill=Y)
        self.listBox = Listbox(self, selectmode = SINGLE, width = 60, height = 10, borderwidth = 0, fg = 'gray27',
                                  bg = 'white', font = ('Andale Mono', 12), highlightcolor = 'white', relief = FLAT, selectbackground = '#A2D5AC')
        self.listBox.pack(side = LEFT, fill = Y)
        scrollBar.config(command = self.listBox.yview)
        self.listBox.config(yscrollcommand=scrollBar.set)
        self.listBox.bind('<<ListboxSelect>>', onselect) #alright so on selection of a song, onselect
        songlist.sort()
        for item in songlist:
			#do some string manip here to add artist as well 
			#still todo
			#need some way of retaining info in box
			edititem = item.replace(".mp3", "")
			self.listBox.insert(END, edititem)
            
            
class sleepBox(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.configure(background = 'black')
		
		button = tk.Button(self, width = 100, height = 100, bg = 'black', relief = FLAT, activebackground = 'black', fg = 'black', command=lambda: controller.show_frame("nowPlaying"))
		button.pack()

class optionsBox(tk.Frame):
	def __init__(self, parent, controller):
		tk.Frame.__init__(self, parent)
		self.controller = controller
		self.configure(background = 'white')
		
		
		backButton = tk.Button(self, width = 100, height = 3, bg = '#A2D5AC', activebackground = '#A2D5AC', highlightthickness =0, bd =0,
		                              fg = 'white', activeforeground = 'white', font = ('Andale Mono', 10, "bold"), text = "back",
		                              command=lambda: controller.show_frame("nowPlaying"))
		backButton.pack()    
		                          
		speakerButton = tk.Button(self, width = 10, height = 5, bg = '#A2D5AC', activebackground = '#A2D5AC', highlightthickness =0, bd =0,
		                              fg = 'white', activeforeground = 'white', font = ('Andale Mono', 10, "bold"), text = "speaker",
		                              command = self.speakerButtonPress)
		speakerButton.place(relx = 0.3, rely = 0.5, anchor = CENTER)
		
		quitButton = tk.Button(self, width = 10, height = 5, bg = '#A2D5AC', activebackground = '#A2D5AC', highlightthickness =0, bd =0,
		                              fg = 'white', activeforeground = 'white', font = ('Andale Mono', 10, "bold"), text = "quit",
		                              command = self.quitButtonPress)
		quitButton.place(relx = 0.7, rely = 0.5, anchor = CENTER)
		
		
		
	def speakerButtonPress(self):
		addedVolume = [164, 166, 169, 171, 173, 175, 177, 
                179, 180, 182, 184, 185, 187, 189, 190, 191, 193, 194, 196, 198, 199, 
                200, 202, 204, 206]
		print "speaker button"
		global volumeList
		global volume
		if len(volumeList) == 23:
			volumeList = volumeList + addedVolume
			print volumeList
		else:
			volumeList = list(set(volumeList) - set(addedVolume))
			volumeList.sort()
			volume = 7
			os.system("amixer set Digital 100")
			print volumeList
		
		
	def quitButtonPress(self):
		print "quit button"
		os.system("sudo killall -v mplayer")
		app.destroy()
		
	

xinput = "xinput set-prop 6 \"Coordinate Transformation Matrix\" 0 -1 1 -1 0 1 0 0 1"
os.system(xinput)
app = mp3App()
app.mainloop()
