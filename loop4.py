#!/usr/bin/python

'''
	Authors: Anubhav Acharya, Ramie Katan
	Date created: 06/10/2021
	Date last modified: 06/25/2021
	Python Version: 3.9.5
'''

#STL imports
import sys, re, csv, os, io
from time import sleep, time
from random import SystemRandom

#pip imports
from serial import SerialException

#custom imports
from connman2 import TConnection, SConnection

#OS Login Credentials
uname = "root"			#the user to login as
pwrd = "admin"			#the password for the user account
#I hate pfsense
pfsense = False
#If the machine needs sudo, put set as True, else set it as false
needSudo = False
#How long to wait for the device to boot
limit=90
#What commands to run after the device has booted succesfully?
commands = ["i2cget -y 0 0x74 0 b", "i2cget -y 1 0x74 0 b", "i2cget -y 2 0x74 0 b", "i2cget -y 3 0x74 0 b", "i2cget -y 4 0x74 0 b", "i2cget -y 5 0x74 0 b"]
#The expected results after running the commands
rslt = [
		'0xf8\r',
		'0xf8\r',
		'0xf8\r',
		'0xf8\r',
		'0xf8\r',
		'0xf8\r'
		]

#The error returned for selecting the wrong i2c device
error = "Error: Read failed\r"

#The i2c bus reading when one of the ports has failed
fail = "0xb8\r"

#PSU Ports the device is connected to
PSUPorts = [1, 2]

#At this point, the script has been setup for usage through command line.
#Good luck.


check = dict()
for i in range(0, len(commands), 1):
	check[commands[i]] = rslt[i]

def help():
	print("\n\nThe script can be used as follows:")
	print("\n\t",sys.argv[0], " <DEVICE> <BAUDRATE> <REPETITIONS>")
	print("\n\tDEVICE:- COMX for windows, /dev/usbX for linux; replace the 'X' with relevant number")
	print("\tBAUDRATE:- A number representing the rate of communication.")
	print("\tREPETITIONS:- Number of times to run the tests for\n\n")
	print("There are parameters that need to be edited before the script is run. Edit the file before use.")
	return

#Regular expressions
off = re.compile(r'^.*reboot:\sPower\sdown.*$')
userNameP = re.compile(r'^.*login:.*$')
bootPrompt = re.compile(r"^.*Press.ESC.for.boot.menu.*$")
passd = re.compile(r'.*0xf8.*')

def setup():
	#this will make sure that the booting device
	#reaches the login prompt
	while bootPrompt.match(connS.readline()) is None:
		pass
	connS.ser.write(b"\033")
	sleep(0.5)
	connS.ser.write(b"2")
	print("Fedora on the USB stick has been selected")

def toLogin():
	start = time()
	failed = False
	while userNameP.match(connS.readline()) is None:
		if (time()-start) > limit:
			print("The device has failed to boot within", limit, "seconds. Boot number:", i+1)
			print("Please mannually check if there is something wrong with the device.")
			print("\n\n\n------Test incomplete------\n\n\n")
			for i in range(0, len(PSUPorts), 1):
				if i%2==0:
					connT.powerOffPort(PSUPorts[i])
				else:
					connT2.powerOffPort(PSUPorts[i])
				failed = True
			break
	
	return failed

def login():
	print("Waiting for the authentication prompt")
	r = toLogin()
	if not pfsense and not r:
		print("Sending username")
		connS.send(uname)
		sleep(1)
		print("Sending password")
		connS.send(pwrd)
		sleep(3.5)
		rslt = connS.readAll()
		if not re.compile(r'^.*Login\sincorrect.*$').match(rslt) is None:
			print("Incorrect username or password supplied.")
			print("Please edit the script with correct values before running.")
			exit()
		print("Login successful")
	elif not r:
		connS.send("8\r", encoding='ascii')
		sleep(2)
		connS.readAll()
		print("Login successful")
	else:
		print("Boot failure")
	return r

def reboot():
	if needSudo:
		connS.send("sudo reboot")
		time.sleep(1)
		connS.send(pwrd)
	else:
		connS.send("reboot")

def poweroff():
	if needSudo:
		connS.send("sudo poweroff")
		time.sleep(1)
		connS.send(pwrd)
	else:
		connS.send("poweroff")

	while off.match(connS.readline()) is None:
		pass

	print("Device powered off successfully")
	return True

def help():
	print("\n\nThe script can be used as follows:")
	print("\n\t",sys.argv[0], " <DEVICE> <BAUDRATE> <REPETITIONS>")
	print("\n\tDEVICE:- COMX for windows, /dev/usbX for linux; replace the 'X' with relevant number")
	print("\tBAUDRATE:- A number representing the rate of communication.")
	print("\tREPETITIONS:- Number of times to run the tests for\n\n")
	print("There are parameters that need to be edited before the script is run. Edit the file before use.")
	return

def loop4():
	logCSV = open("loop4.csv", "w", newline="")
	writer = csv.writer(logCSV)
	writer.writerow(["Loop 4"])
	log = ["Loop 4"]

	for i in range(0, reps, 1):
		print("loop4: Test", i+1, "starting now...")
		
		r = SystemRandom()
		
		result = ""

		for k in range(0,2,1):
			if result != "":
				result+="|"

			print("Turning the PSU ports on")

			connT.powerOnPort(PSUPorts[0])
			connT.powerOnPort(PSUPorts[1])

			print("Waiting for the boot prompt...")
			start = time()

			setup()
			failed = login()

			if failed:
				failed = False
				result+=("Boot failure")

				connT.powerOffPort(PSUPorts[1])
				connT.powerOffPort(PSUPorts[0])

				sleep(120)

				continue
			
			end = time()-5
		
			failed = True
			
			print("Device took", (end-start), "seconds to boot up.")
			print("Running the test commands now")
			for cmd in commands:
				if (cmd == "lsblk" or cmd == "dmidecode -t 0,1,2,3") and needSudo:
					connS.justSend("sudo "+cmd)
					sleep(1)
					rslt = connS.send(pwrd)
				else:
					rslt = connS.send(cmd)

				rslt = rslt.split("\n")

				if error in rslt:
					continue

				if fail in rslt:
					result+="failed"
					failed = True
				elif check[cmd] in rslt:
					result+="passed"
					failed = False

			if failed:
				print("One of the ports failed this run.")
			else:
				print("Nothing seemingly failed this run.")

			print("Powering off the device now")
			poweroff()
			
			connT.powerOffPort(PSUPorts[1])
			connT.powerOffPort(PSUPorts[0])

			if k%2 == 0:
				sleep(delay:=r.randint(1000,3000)/1000)
			print("Delayed for", delay, "seconds")

		writer.writerow([result])
		log.append(result)

		if i+1 < reps:
			print("Test", i+1, "completed.")
			print("Powering the PSU Port off and waiting for 120 seconds")
			sleep(5)
			print("Moving on to test",i+2,"\n")
		else:
			print("Test", i+1, "completed. All done. Moving on")
			sleep(5)

	logCSV.flush()
	logCSV.close()
	return log

def main():
	logCSV = open("log.csv","w",newline="")
	writer = csv.writer(logCSV)
	log = list()
	if len(PSUPorts) == 0:
		print("Please enter the ports the device is connected to before running the script.")
		print("Exiting now...")
		return

	try:
		print("\nInitializing Serial connection with the device....")
		global connS
		connS = SConnection(sys.argv[1],int(sys.argv[2]))
		print("Done")
	except SerialException:
		print("A connection with the device was not established. Please advise.")
		return
	except ValueError:
		print("The baudrate can only be a pure number.")
		return
	
	try:
		print("\nInitializing Telnet connection with the PSU....")
		global connT
		connT = TConnection()
		print("Done")
	except OSError:
		print("Connetion with the PSU over Telnet was not established. Please advise.")
		exit()
	
	try:
		global reps
		reps = int(sys.argv[3])
	except ValueError:
		print("Number of repetions can only be a number.")
		exit()

	for p in PSUPorts:
		if p < 1 or p > 4:
			print("The PSU port the device is connected to was out of bounds.")
			print("Please enter the proper port numbers; between 1 and 8")
			exit()

	

	print("\n")
	print("The series of tests will begin now. Good luck!!\n")

	print("Loop 4 initiating now")
	log.append(loop4())
	print("Loop 4 complete.")

	tmp1 = list()
	tmp2 = list()
	for i in range(0, len(log[0]), 1):
		for j in range (0,len(log),1):
			tmp1.append(log[j][i])
		tmp2.append(tmp1)
		tmp1 = []

	writer.writerows(tmp2)
	logCSV.flush()
	logCSV.close()

	print("\nAll tests completed. The log is available as log.csv in the same directory as the script.")

if __name__ == '__main__':
	if len(sys.argv) == 4:
		main()

	else:
		help()