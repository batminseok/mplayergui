import mutagen
from mutagen.mp3 import *
from mutagen.id3 import ID3
import os
import subprocess

#f = MP3("/home/pi/Music/Resources/Just.mp3") #nice n sidify

#print mutagen.File("/home/pi/Music/Resources/Just.mp3").keys() 

#try: 
#	artwork = f["APIC:thumbnail"].data #ok so sort depending on wether theyre musicbrainz or not 
#except: 
#	print "whatever"
	
#try:
#	artwork = f["APIC:"].data
#except:
#	print "whatever"

#try:
#	with open('hmm.png', 'wb') as img:
#		img.write(artwork)
#except:
#	print "nope"
	
#print f["TALB"] #album
#print f["TIT2"] #title
#print f["TPE1"] #artist


failist = []

songlist = []

for file in os.listdir("/home/pi/Music/Resources"):
    if file.endswith(".mp3"):
        songlist.append(file)

for i, line in enumerate(songlist): #check song info
	formatted = line.rstrip()
	filename = formatted.replace('.mp3', '')
	picfilename = filename + '.png'
	mp3 = MP3("/home/pi/Music/Resources/" + formatted)
	try: 
		print mp3["TIT2"]
		print mp3["TPE1"]
	except:
		print "FAILED: " + formatted
		failist.append(formatted)
		
print failist


for i, line in enumerate(songlist): #create pngs
	print i
	print line
	formatted = line.rstrip()
	filename = formatted.replace('.mp3', '')
	picfilename = filename + '.png'
	mp3 = MP3("/home/pi/Music/Resources/" + formatted)
	total = 0
	substring = "convert " + filename + ".png -resize 100x100 " + filename + ".gif"
	print substring
	try: 
		artwork = mp3["APIC:thumbnail"].data #ok so sort depending on wether theyre musicbrainz or not 
		with open(picfilename, 'wb') as img:
			img.write(artwork)
	except: 
		total += 1  
			
	try:
		artwork = mp3["APIC:"].data
		with open(picfilename, 'wb') as img:
			img.write(artwork)
	except:
		total += 1
		
	if total ==2:
		failist.append(formatted)
			
print failist

#mogrify -format gif -resize 100x100 *.png

			
		

