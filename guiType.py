import os, time, platform, importlib
from datetime import datetime,timedelta
from tkinter import *

import ioServ
import osk

root = Tk() # main window
nuWin = None # new user window
qtWin = None # quit password window

# *F=frame, *S=scroll, *L=list, *B=button, *T=label, *E=entry
nameL = infoT = logoImgs = logoL = None
logoCurrent = -1 # start on 0, since updateLogo adds 1

#root.config(bg='#000000')
root.title('PhyxtGears1720io')
root.geometry('800x600')  # 1024x768 # set resolution
# glblBGC = '#343d46'
if platform.system() != 'Windows' and platform.system() != 'Darwin':
	root.attributes('-fullscreen', True)

opts = ioServ.loadOpts() # load options from file

try:
	os.mkdir(opts['pathTime'])
except:
	pass

ioServ.mkfile(opts['usernameFile'])

	
def makeNewUserWindow():  # new user window
	global root, nuWin
	if nuWin != None and Toplevel.winfo_exists(nuWin): return

	nuWin = Toplevel(root) # make window
	nuWin.attributes('-topmost',1)
	nuWin.title('Create new user')
	#nuWin.geometry('460x160')

	inputF = Frame(nuWin) # frame for input boxes
	buttnF = Frame(nuWin) # frame for buttons
	jobF = Frame(nuWin) # frame for choosing between student and mentor
	vkeyF = Frame(nuWin, pady=8) # on screen keyboard frame

	Label(inputF, text='Fullname: ', font='Courier 14').grid(sticky=E, padx=2, pady=2)
	Label(inputF, text='Initials: ', font='Courier 14').grid(sticky=E, padx=2, pady=2)

	nuFullE = Entry(inputF, font='Courier 18', width=42)  # full name textbox
	nuUserE = Entry(inputF, font='Courier 18', width=42)  # username  textbox

	def setVK(choice): # function to set which input box the virtual keyboard puts text in
		if   choice == 1: vkey.attach = nuFullE
		elif choice == 2: vkey.attach = nuUserE
	nuFullE.bind('<FocusIn>', lambda e: setVK(1))
	nuUserE.bind('<FocusIn>', lambda e: setVK(2))

	nuFullE.grid(row=0, column=1)
	nuUserE.grid(row=1, column=1)
	inputF.pack()

	nuErrT = Label(nuWin, font='Courier 14', text='', fg='red')  # if theres an error with the name (ie name exists or not a real name) show on screen
	nuErrT.pack()

	# the different jobs a member can have, currently only student or mentor
	jobOption, j = ['Student','Mentor','Adult'], 0
	jobChoice = IntVar(); jobChoice.set(0)
	for job in jobOption: # generate an option for every job in jobOption
		Radiobutton(jobF,text=job,font='Courier 14 bold', variable=jobChoice,value=j).grid(row=0,column=j)
		j += 1
	jobF.pack()

	def finishNewUser(): # perform checks on names for when the user is finished
		errmsg, user, full = 'None', nuUserE.get(), nuFullE.get()

		if user == '' or full == '': errmsg = 'Err: All boxes must be filled'
		elif ioServ.checkNameDB(full): errmsg = 'Err: Fullname already exists.'
		elif ioServ.checkNameDB(user): errmsg = 'Err: Username already exists.'

		if errmsg == 'None':
			ioServ.addNameDB(full.title(), user.lower(), jobOption[jobChoice.get()])
			refreshListboxes()
			alertWindow(text='Make sure you, '+full.title()+', sign in!', fg='orange')
			nuWin.destroy()
		else:
			nuErrT.config(text=errmsg, fg='red')

	finB = Button(buttnF, text='Create User', font='Courier 14', fg='blue', width=16, command=finishNewUser)
	canB = Button(buttnF, text='Cancel',      font='Courier 14', fg='red',  width=16, command=nuWin.destroy)
	finB.grid(row=0, column=1)
	canB.grid(row=0, column=0)
	buttnF.pack()

	vkey = osk.vk(parent=vkeyF, attach=nuFullE)  # on screen alphabet keyboard
	vkeyF.pack()



def refreshListboxes(n=None): # whenever someone signs in/out or theres a new user
	global nameL, infoT
	if n=='all' or n==None:
		nameL.delete(0, END)
		ioServ.sortUsernameList()

		nameIO = ''
		timet = 0
		typeIO = 'N'
		select = 0

		for line in open(opts['usernameFile']):
			nameIO = line.strip().split('|')[0]
			try:
				with open(opts['pathTime'] + nameIO.replace(' ', '') + '.txt', 'r+') as f:
					timet = min( int(round(ioServ.calcTotalTime(nameIO)/3600)), 999 )
					timeIO = ' '*max(3-len(str(timet)),0) + str( timet )
					typeIO = f.readlines()[-1][0]  #iolist.insert(END, f.readlines()[-1][0])
			except:
				timeIO = '   '
				typeIO = 'N'
			nameL.insert(END, nameIO + ' ' * (35 - len(nameIO)-4) + timeIO + ' ' + typeIO)
			nameL.itemconfig(select, {'fg' : hoursToColor(nameIO)})
			timet = 0
			select += 1
	elif n=='single':
		select = nameL.curselection()[0]
		nameIO = nameL.get(select)[:-5]
		timet = 0
		typeIO = 'N'
		nameL.delete(select,select)
		try:
			with open(opts['pathTime'] + nameIO.replace(' ', '') + '.txt', 'r+') as f:
				timet = min( int(round(ioServ.calcTotalTime(nameIO)/3600,0)), 999 )
				timeIO = ' '*max(3-len(str(timet)),0) + str( timet)
				typeIO = f.readlines()[-1][0]  #iolist.insert(END, f.readlines()[-1][0])
		except:
			timeIO = '   '
			typeIO = 'N'
		nameL.insert(select, nameIO + timeIO + ' ' + typeIO)
		nameL.itemconfig(select, {'fg' : hoursToColor(nameIO)})
		nameL.see(select+1)

def hoursToColor(name):
	timet,weekly = ioServ.calcSeasonHours(name)
	timet /= 3600

	print(name, timet//1,(timet-weekly*8)//1)
	# CHANGE THIS TO USE PER DAY OR PER HOUR CALCULATION SO THAT PEOPLE DONT HAVE BAD COLORING
	if weekly != 0: timet -= weekly*8 # in season

	if timet >= 6 :
		return '#00bf00' # green
	elif 2 < timet < 6:
		return '#FFAF00' # yellow orange
	else:
		return '#FF0000' # red
	return '#000000'



def ioSign(c):
	global nameL
	if len(nameL.curselection()) == 0:
		alertWindow(text='Nothing Selected!', fg='orange')
		return
	nameIO = nameL.get(nameL.curselection()[0])[:-5]
	timeIO = time.strftime(opts['ioForm'])
	lines = []
	open(opts['pathTime'] + nameIO.replace(' ', '') + '.txt', '+a').close()
	with open(opts['pathTime'] + nameIO.replace(' ', '') + '.txt', '+r') as f: lines = [line.strip() for line in f]

	if lines:
		theNow = datetime.now()
		theIOA = datetime.strptime(lines[-1][5:], opts['ioForm'])
	autoClocked = False

	ioServ.mkfile(opts['pathTime'] + nameIO.replace(' ', '') + '.txt')  # make file if it doesn't exist

	lim = [int(x) for x in opts['autoClockLim'].split(':')]
	inTimeFrame = lines and theIOA < theNow < (theIOA.replace(hour=lim[0], minute=lim[1], second=lim[2], microsecond=0) + timedelta(days=1))

	if lines and lines[-1][0] == 'a' and c == 'o' and inTimeFrame:
		print('RECOVERING')
		# RECOVERING AUTOCLOCKOUT
		with open(opts['pathTime'] + nameIO.replace(' ', '') + '.txt', 'w+') as f:
			f.write('\n'.join(lines[:-1]) + '\n' + c + ' | ' + timeIO + '\n')
		# note for future annoucement system: have annoucements over phone system annoucing the time till autoclockout cutoff
		# ie: "it is 4:00am, 1 hour till autoclockout cutoff. please be sure to sign out and sign back in to get the hours."
		alertWindow(text=nameIO.split()[0] + ' signed out proper!', fg='Green')
	elif lines and (lines[-1][0] == c or (lines[-1][0]=='a' and c=='o')):
		# DOUBLE SIGN IN/OUT
		if c == 'i':
			alertWindow(text=nameIO.split()[0] + ' is already signed in!', fg='orange')
		elif c == 'o':
			if lines[-1][0] == 'o':   alertWindow(text=nameIO.split()[0] + ' is already signed out!', fg='orange')
			elif lines[-1][0] == 'a': alertWindow(text=nameIO.split()[0] + ' was auto-signed out!', fg='orange')
	elif not lines and c == 'o':
		# NEVER SIGNED IN BEFORE
		alertWindow(text=nameIO.split()[0] + ' has never signed in!', fg='orange')
	else:
		# NORMAL SIGN IN/OUT
		with open(opts['pathTime'] + nameIO.replace(' ', '') + '.txt', 'a+') as f:
			f.write(c + ' | ' + timeIO + '\n')
		hours = str(round(ioServ.calcTotalTime(nameIO.replace(' ', '')) / 3600, 2)) # calculate total time in seconds then convert to hours (rounded 2 dec places)
		weekh = str(round(ioServ.calcWeekTime( nameIO.replace(' ', '')) / 3600, 2)) # calculate current week time
		if c == 'i':
			alertWindow(text=nameIO.split()[0] + ' signed in! '  + hours + ' hours.\n'+weekh+' of 8 hours.', fg='Green')
		elif c == 'o':
			alertWindow(text=nameIO.split()[0] + ' signed out! ' + hours + ' hours.\n'+weekh+' of 8 hours.', fg='Red')
		# note for out signio: even if there is an issue one signout, show an error but still log the out. this was robby's idea.

	refreshListboxes('single')



def alertWindow(text='',fg='orange',font='Courier 14 bold'):
	wind = Toplevel(root) # new window
	wind.geometry('320x120') # set resolution
	wind.overrideredirect(1) # make window borderless

	# add text to window
	Label(wind, text=text,fg=fg,font=font,height=6,wraplength=300,justify=CENTER).place(x=160,y=60,anchor=CENTER)

	wind.after(3000, wind.destroy) # exit window after 3 seconds



def confirmQuit():  # quit program window with passcode protection
	global root, opts, qtWin
	if qtWin != None and Toplevel.winfo_exists(qtWin): return
	qtWin = Toplevel(root)
	qtWin.title('Quit?')
	Label(qtWin, text='Enter AdminPass\nto quit.', font='Courier 16 bold').pack(pady=2)
	passEntry = Entry(qtWin, font='Courier 14', width=10, show='*')
	passEntry.pack(pady=2)

	def areYouSure():
		if passEntry.get() == opts['adminPass']:
			root.destroy()

	buttonF = Frame(qtWin)
	quitit = Button(buttonF, text='Quit',  font='Courier 14 bold', fg='red', command=areYouSure)
	cancit = Button(buttonF, text='Cancel', font='Courier 14 bold', fg='blue', command=qtWin.destroy)
	quitit.grid(column=0, row=0)
	cancit.grid(column=1, row=0)
	buttonF.pack(pady=2)
	vnum = osk.vn(parent=qtWin, attach=passEntry)

def updateLogo():
	global logoImgs, logoL, logoCurrent
	logoCurrent += 1
	if logoCurrent >= len(logoImgs): logoCurrent = 0
	logoL.config(image=logoImgs[logoCurrent])
	root.after(5000,updateLogo)



def main():
	# *F = frame, *S = scroll, *L = list, *B = button, *T = text
	global nameL, infoT, logoImgs, logoL
	listF = Frame(root)
	listS = Scrollbar(listF, orient=VERTICAL)
	nameL = Listbox(listF, selectmode=SINGLE, yscrollcommand=listS.set, font='Courier 18')
	nameL.config(width=36, height=20)
	listS.config(command=nameL.yview, width=52)

	form = 'Name                          hrs i/o'
	Label(listF, text=form, font='Courier 18 bold',anchor=W,justify=LEFT,width=40).pack()
	listS.pack(side=RIGHT, fill=Y)
	nameL.pack(side=LEFT, fill=BOTH, expand=1)
	listF.pack(side=LEFT, padx=12)

	logoImgs = [PhotoImage(file='assets/1720.gif'),PhotoImage(file='assets/30483-2.gif'),PhotoImage(file='assets/34416-4.gif')]
	Label(root, text='PhyxtGears1720io', font='Courier 12').pack(pady=4)
	logoL = Label(root, image=logoImgs[0]); logoL.pack()
	updateLogo()

	f = 'Courier 16 bold'
	ioF = Frame(root)
	iIOB = Button(ioF, text='IN',  font=f, bg='green',fg='white', command=lambda: ioSign('i'), width=12, height=2)
	oIOB = Button(ioF, text='OUT', font=f, bg='red',  fg='white', command=lambda: ioSign('o'), width=12, height=2)
	infoT = Label(ioF, text='', font=f, height=5, wraplength=0, justify=CENTER) # white space generator ftw
	newB = Button(ioF, text='New User', font=f, bg='blue', fg='white', command=makeNewUserWindow, width=12, height=2)

	iIOB.pack(pady=8)
	oIOB.pack(pady=8)
	infoT.pack()
	newB.pack(pady=4)
	ioF.pack()

	Button(text='QUIT', font='Courier 16 bold', height=1, fg='red', command=confirmQuit).pack(side=RIGHT, padx=12)
	Button(text='UPDATE', font='Courier 16 bold', bg='orange',fg='white', command=lambda: refreshListboxes(), height=1).pack(side=RIGHT)

	refreshListboxes()

	root.mainloop()


if __name__ == '__main__':
	main()
