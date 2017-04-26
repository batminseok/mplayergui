import Tkinter as tk
from Tkinter import * 

root = tk.Tk()

photo = PhotoImage(file = "albumart.gif")

label = Label(image = photo)
label.image = photo
label.pack()

root.mainloop()
