"""
PhyXTGearsTimeClock.py

Main program for students to sign in and out.

V2: Added clicking
V3: Added graphics class, restructured all code. Auto-update before each sign-in.
"""


import ctypes
import os
import time
from importlib import reload

import Calculations_Service
import graphics
from myFunctions import myInput, myRound
from optsFile import opts

reload(graphics)

open(opts['name.txt'], 'a').close()

# To check if a name is in a valid format e.g. "John Smith"


def checkName(firstLastName):
	error = False
	firstLastNameList = firstLastName.split()
	if len(firstLastNameList) < 2:
		error = True
	else:
		for item in firstLastNameList:
			if item[0].islower():
				error = True
	return error


def getMinutes(): return str(int(time.strftime('%H')) * 60 + int(time.strftime('%M')))


def newName(allList):
	name = input("Enter your full name. Ex: 'Bob Smith' => ")
	while checkName(name) and name in allList and name != "c":
		print("Error! Invalid name format!")
		name = input("Enter your full name. Ex: 'Bob Smith' => ")
	if name != "c":
		print()
		print("Now enter a username, which you can use to sign in instead of your full name.")
		while True:
			username = input("Must be three or more characters => ")
			if not len(username) >= 3:
				print("Error: Name is too short")
			elif username in allList:
				print("Error: Name already exists")
			else:
				break
		print("Student or mentor?")
		choice = myInput("Enter s or m => ", "Invalid input!", strs=["s", "m"])

		# Code for writing info to usernameFile:
		with open(opts['name.txt'], 'a') as nameFile:
			jobOpt = {'s':'Student', 'm':'Mentor', 'a':'Adult'} # , 'p':'Programmer', 
			if jobOpt[choice] != None: nameFile.write(name + "|" + username + "|"+jobOpt[choice]+"\n")
			else: nameFile.write(name + "|" + username + "|None\n")
		allList += [name, username]
	else:
		name = None
	return name


def animate(name, io, today=None, total=None):
	turtle.fillcolor('black')
	drawRectangle(0, 1000, 1000, 1000)
	turtle.fillcolor('green')
	drawRectangle(50, 575, 900, 150)
	text = "Signing " + name + " " + io.lower() + "..."
	writeText(text, 500, 450, 25)
	inSpeed = 0.07
	outSpeed = 0.15
	if today == total == None:
		speed = inSpeed
	else:
		speed = outSpeed
	loading = "_"
	for i in range(15):
		writeText(loading, 500, 442, 40)
		writeText(loading, 500, 438, 40)
		writeText(loading, 500, 434, 40)
		writeText(loading, 500, 430, 40)
		time.sleep(speed)
		loading += "_"
		if i == 1 and today != None:
			turtle.fillcolor('green')
			drawRectangle(100, 350, 800, 100)
			text = "Today's Hours: " + str(today)
			writeText(text, 500, 250, 24)
# time.sleep(1)
		if i == 2 and total != None:
			turtle.fillcolor('green')
			drawRectangle(100, 175, 800, 100)
			text = "Total Hours: " + str(total)
			writeText(text, 500, 75, 24)
# time.sleep(1)
	if speed == outSpeed:
		time.sleep(3)


# These lines initiate two global variables: "usernamelist","allList"
with open(opts['name.txt'], 'r') as nameFile:
	usernamelist = nameFile.readlines()
	for i in range(len(usernamelist)):
		usernamelist[i] = usernamelist[i].strip("\n").split("|")

allList = ["new"]
for name in usernamelist:
	allList.append(name[0])
	allList.append(name[1])


# [x,y,size],[x,y,xLen,yLen]
sizes3 = {"IN": {2: [250, 400, 85],
				 1: [50, 800, 400, 500]},
		  "OUT": {2: [750, 400, 85],
				  1: [550, 800, 400, 500]},
		  "CANCEL": {2: [500, 45, 35],
					 1: [200, 125, 600, 75]}}
sizes2 = {"IN": {2: [250, 400, 85],
				 1: [50, 350, 400, 500]},
		  "OUT": {2: [750, 400, 85],
				  1: [550, 350, 400, 500]},
		  "CANCEL": {2: [500, 45, 35],
					 1: [200, 65, 600, 125]}}
if opts['onScreenKeyBoard']:
	sizes = sizes2
else:
	sizes = sizes3


def getIO():
	screen = {'width': 0.5, 'height': 0.5, 'startX': 0.5, 'startY': 0}
	ioPadding = 50
	otherPadding = 13
	if not opts['onScreenKeyBoard']:
		screen['height'] = 1
		ioPadding = 135
		otherPadding = 35
	w = graphics.Graphics("1720 Time Clock", "black", screen)
	w.addButton(90, 150, 360, 450, "white", "IN", "green", ioPadding)
	w.addButton(550, 150, 360, 450, "white", "OUT", "red", ioPadding)
	w.addButton(90, 750, 360, 150, "white", "Cancel", "blue", otherPadding)
	w.addButton(550, 750, 360, 150, "white", "Options", "blue", otherPadding)
	return w.getClick() or "none"


def recordData(name, io):
	systemtime = getMinutes().rjust(4) + ' of day ' + time.strftime('%j')
	readtime = time.strftime('%I:%M:%S %p, %A, %B %d %Y')
	timeHours = time.strftime('%I:%M %p')
	timeRest = time.strftime('%A, %B %d')
	print("\n" + name + " " + io + " " + timeHours)
	print(timeRest + "\n")
	l = readtime.split()
	for i in range(1, len(l)): l[i] = " " + l[i]
	readtime = l[0] + l[1] + l[2].rjust(11) + l[3].rjust(10) + l[4] + l[5]
	
	if not os.path.isdir(opts["path"]): os.mkdir(opts["path"])

	if io == "IN":  # Signing in
		with open(opts['path']+name+'.txt','a') as oldFile: oldFile.write('I | '+systemtime+' | '+readtime+'\n')
		return None,None
	elif io == "OUT":  # Signing out
		try:  # Try because the file might be empty
			with open(opts['path']+name+'.txt', 'r') as oldFile:
				l = oldFile.readlines()[-1].split()
				inList = [l[0], l[2], l[5]]
		except:
			inList = ['O']
		
		doCalc = True
		if inList[0] == 'O':
			cur,bck = '',''
			with open(opts['path']+name+'.txt', 'r') as oldFile:
				rl = oldFile.readlines()
				cur = rl[-1].split()
				bck = rl[-2].split()
			if cur[2]==bck[2] and cur[5]==bck[5]: 
				with open(opts['path']+name+'.txt', 'r') as oldFile:
					rl = oldFile.readlines()
					del rl[-1]
					rl = '\n'.join(rl)
				with open(opts['path']+name+'.txt', 'w') as oldFile:
					oldFile.write(rl)
			else:
				print("Didn't sign in!")
				hoursToday = 0
				doCalc = False
		if doCalc==True:
			day = int(time.strftime('%j'))
			if day == int(inList[2]):
				currentMinutes = int(getMinutes()) - int(inList[1])
			else:  # Different Day
				currentMinutes = 1440 - int(inList[1]) + int(getMinutes())
				for i in range(day - int(inList[2]) - 1): currentMinutes += 1440
			hoursToday = round(currentMinutes / 60,2) # myRound(currentMinutes / 60, 2)

		with open(opts['path']+name+'.txt','a') as file: file.write('O | '+systemtime+' | '+readtime+'\n')

		reload(Calculations_Service)
		hoursTotal = round(Calculations_Service.calculateSingle(name), 2)
		print("Today's Hours:", hoursToday)
		print("Total Hours:", hoursTotal)
		return hoursToday, hoursTotal


def otherOptions(): print("THIS DOES NOTHING YET!")#print("In otherOptions, processing")

def getProperName(name):
	spln = ""
	for line in open(opts["name.txt"]):
		if name in line: spln = line
	spln = spln.split("|")
	return spln[0]


def getName():
	global allList
	print("\n##############################################################\n")
	print("To add a new person, type 'new'")
	while True:
		name = input("Enter a name => ")
		if name == "": print("Error: Name is empty!")
		elif not name in allList + ["quit", "admin", "new"]: print("Error: Name not found! Try again.")
		else: break
	if name == "new":
		name = newName(allList)
	elif name == "quit":
		pass
	elif name == "admin":
		if input("Password: ")==opts["adminPass"]:
			reload(Calculations_Service)
			Calculations_Service.main()
			name = None
	else:
		name=getProperName(name)
	return name
	


def main():
	name = ""
	while not name in ["quit","admin"]:
		name,io = getName(),getIO()
		if io in ["IN", "OUT"]: today, total = recordData(name, io) # animate(name,io,today,total)
		elif io == "Options": otherOptions()
		elif io == "Cancel": pass # name="cancel"
		else: print("===== error with IO function =====")
		


if __name__ == "__main__": main()

'''
	add auto sign-out at 12 am, make it log zero hours for that person.
	add check for if sign out after 12, change the zero hours to the proper hours logged
'''