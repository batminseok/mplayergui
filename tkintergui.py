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
import thread

#subprocess.Popen("amixer set Digital 50%", shell = True) volume eventually 

started = 0 #for keeping track of start or not
songNumber = 0 #for keeping track of place in playlist
paused = False

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

    

class mp3App(tk.Tk):

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
        
        self.seconds = 0
        
        playphoto = ImageTk.PhotoImage(file = "play_button.png")
        forwardphoto = ImageTk.PhotoImage(file = "forwardarrow.png")
        backwardphoto = ImageTk.PhotoImage(file = "backarrow.png")
        
        self.secv = StringVar()
        self.minv = StringVar()
        self.lengthv = StringVar()
        
        self.configure(background = 'white')

        self.switchbutton = tk.Button(self, height = 100, width = 100, highlightthickness = 0, bd = 0, bg = 'white',
                            activebackground = 'white', relief = SUNKEN, command=lambda: controller.show_frame("songList"))
        self.switchbutton.place(relx=0.5, rely=0.20, anchor= CENTER)
        
        self.songTitle = Label(self, text = "Song Title", bg = 'white', font = ('Andale Mono', 10,"bold"), fg = 'gray27')
        self.songTitle.place(relx = 0.5, rely = 0.4, anchor = CENTER)
        
        self.artistName = Label(self, text = "Artist Name", bg = 'white', font = ('Andale Mono', 10), fg = 'gray27')
        self.artistName.place(relx = 0.5, rely = 0.46, anchor = CENTER)
        
        s = ttk.Style()
        s.theme_use('alt')
        s.configure("TProgressbar", foreground = 'white', background = 'white', troughcolor = 'gray27', thickness = 5,)
        self.progressBar = ttk.Progressbar(self, style = "TProgressbar", orient = "horizontal", 
                               length = 350, mode = "determinate", maximum = 100)
        self.progressBar.place(relx = 0.5, rely = 0.6, anchor = CENTER)
        
        self.timerLabel = Label(self, textvariable = self.secv, bg = 'white', font = ('Andale Mono', 10), fg = 'gray27')
        self.timerLabel.place(relx = 0.09, rely = 0.6, anchor = CENTER)
        
        self.lengthLabel = Label(self, textvariable = self.lengthv, bg = 'white', font = ('Andale Mono', 10), fg = 'gray27')
        self.lengthLabel.place(relx = 0.91, rely = 0.6, anchor = CENTER)
        
        backwards = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.backPress)
        backwards.place(relx=0.35, rely=0.8, anchor= CENTER)
        backwards.config(image = backwardphoto)
        backwards.image = backwardphoto
        
        play = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.playPress)
        play.place(relx=0.5, rely=0.8, anchor= CENTER)
        play.config(image = playphoto)
        play.image = playphoto
        
        forwards = tk.Button(self, height = 70, width = 70, bg = 'white', activebackground = 'white', 
                               highlightthickness = 0, bd = 0, command = self.forwardPress)
        forwards.place(relx=0.65, rely=0.8, anchor= CENTER)
        forwards.config(image = forwardphoto)
        forwards.image = forwardphoto
        
        
        
        
        
        
    def backPress(self):
        
        k = PyKeyboard()
        
        if started == 1:
            print "back button pressed"
            os.system("bash mplayerbash.sh key_down_event 60")
            
            self.progressBar.stop()
            self.after_cancel(self.count)
            self.decreaseSongNumber()
            self.secv.set('0:00')
        
        
    def playPress(self):
        
        global started
        global songNumber
        k = PyKeyboard()
        
        if started == 0: #start tunes
			
            createPlaylist()
            callmplayer()
            
            self.editInfo() #runs main looping through music loop
            
            started = 1
            
        elif started == 1: #song is playing, button pauses
            global paused
            print "playing"
            
            if paused == False: #if playing
                os.system("bash mplayerbash.sh key_down_event 112")
                print "bash called"
                #change icon
                #cancel after_timer 
                self.after_cancel(self.count)
                step_amount = ((1 - (self.seconds / self.length)) * 100)
                print str(step_amount)
                self.progressBar.stop()
                print "paused"
                self.progressBar.step(step_amount) #step is a %
                paused = True
            else:
                os.system("bash mplayerbash.sh key_down_event 112")
                print "bash called"
                #change icon
                self.timer()
                self.progressBar.start(self.intervalLength)
                print "playing"
                paused = False
                
        
    def forwardPress(self):
        
        if started == 1:
            
            k = PyKeyboard()
            print "forward button pressed"
            os.system("bash mplayerbash.sh key_down_event 62")
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
            #could put placeholder image here/or just sort art out 
            
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
        
   	
        
        


class songList(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        button = tk.Button(self, text="back",
                           command=lambda: controller.show_frame("nowPlaying"))
        button.pack()



if __name__ == "__main__":
    app = mp3App()
    app.mainloop()
