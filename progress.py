#!/usr/bin/python
import Tkinter
import time

class App(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize() 

    def initialize(self):#This is where the info for the main window starts.

        self.secv = Tkinter.StringVar()
        self.timerv = Tkinter.StringVar()
        self.timer = 20
        

        self.testlabel1 = Tkinter.Label(self, textvariable=self.timerv).grid(column=0, row=0, columnspan=2, sticky='W'+'E')
         
        if self.timer == 20:
            self.test()

    def test(self):
        self.s = self.timer%60
        self.secv.set(self.s)
        self.timerv.set(self.secv.get() + 's')
        kill = self.after(1000, self.test) 
        if self.timer == 0:
            self.after_cancel(kill)
        self.timer -= 1

        
    



if __name__ == "__main__":
    app = App(None)
    app.title('Study Night')
    app.geometry('+100+70')
    app.mainloop()
