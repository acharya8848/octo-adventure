#!/usr/bin/python

'''
	Authors: Anubhav Acharya, Ramie Katan
	Date created: 06/10/2021
	Date last modified: 06/25/2021
	Python Version: 3.9.5
'''

#STL imports
import sys, re, csv, os, io, traceback
from time import sleep, time
from random import SystemRandom

#pip imports
from serial import SerialException

#custom imports
from connman2 import TConnection, SConnection

#OS Login Credentials
uname = "root"			#the user to login as
pwrd = "admin"			#the password for the user account
#If the machine is running pfSense, set this to True, else set it to False; As a sidenote, I hate pfSense
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
fail1 = "0xb8\r"
fail2 = "0x78\r"

#PSU Ports the device is connected to
PSUPorts = [1, 4]

#At this point, the script has been setup for usage through command line.
#Good luck.

#Building a hash map using commands and the respective results
check = dict()
for i in range(0, len(commands), 1):
	check[commands[i]] = rslt[i]

#Verbose log of the device output
v = open("Verbose Log 9.txt", "w")

#Random number generator
r = SystemRandom()

#Regular expressions
off = re.compile(r'^.*reboot:\sPower\sdown.*$')
userNameP = re.compile(r'^.*login:.*$')
bootPrompt = re.compile(r"^.*Press.ESC.for.boot.menu.*$")
passd = re.compile(r'.*0xf8.*')

def verbose(end:bool=False):
	v.write(connS.ser.read().decode('ascii', errors='ignore'))
	if end:
		v.flush()
		v.close()

def fix():
	for i in range(0,6,1):
		cmd = "i2cset -y "+str(i)+" 0x5b 0x06 0x01"
		connS.send(cmd)

def setup():
	#this will make sure that the booting device
	#reaches the login prompt
	while bootPrompt.match(read:=connS.readline()) is None:
		v.write(read)
	connS.ser.write(b"\033")
	sleep(0.5)
	connS.ser.write(b"2")
	print("Fedora on the USB stick has been selected")

def toLogin():
	start = time()
	failed = False
	while userNameP.match(read:=connS.readline()) is None:
		v.write(read)
		if (time()-start) > limit:
			print("The device has failed to boot within", limit, "seconds.")
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
		v.write(rslt)
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
		v.write(connS.send("sudo reboot"))
		time.sleep(1)
		v.write(connS.send(pwrd))
	else:
		v.write(connS.send("reboot"))

def test():
	failed = "0x38"
	for cmd in commands:
		rslt = connS.send(cmd)
		v.write(rslt)
		rslt = rslt.split("\n")

		if error in rslt:
			continue

		if check[cmd] in rslt:
			print("System report: 0xf8")
			failed = "0xf8"
		elif fail1 in rslt:
			print("System report: 0xb8")
			failed = "0xb8"
		elif fail2 in rslt:
			print("System report: 0x78")
			failed = "0x78"

	return failed

def poweroff():
	if needSudo:
		v.write(connS.send("sudo poweroff"))
		time.sleep(1)
		v.write(connS.send(pwrd))
	else:
		v.write(connS.send("poweroff"))
	start = time()
	while off.match(read:=connS.readline()) is None:
		v.write(read)
		if time() - start > 30:
			print("Device failed to report poweroff within 30 seconds. Cutting power now.")
			break
	v.write(read)
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

def loop9():
	v.write("\n\nLoop 9 starts here\n\n")
	logCSV = open("loop9.csv", "w", newline="")
	writer = csv.writer(logCSV)
	writer.writerow(["Loop 9"])
	log = ["Loop 9"]

	for i in range(0, reps, 1):
		v.write("\nLoop 9 test "+str(i+1)+" starts here.\n")
		print("loop9: Test", i+1, "starting now...")
		
		result = ""

		for k in range(0,2,1):
			if result != "":
				result+="|"
			
			result += (str(time())+"/")

			print("Turning the PSU ports on")

			connT.powerOnPort(PSUPorts[0])

			print("Waiting for the boot prompt...")
			start = time()

			setup()
			failed = login()

			if failed:
				result+=("Boot failure")

				connT.powerOffPort(PSUPorts[1])
				connT.powerOffPort(PSUPorts[0])
				
				logCSV.flush()

				sleep(120)

				continue
			
			end = time()-5
		
			failed = True
			
			print("Device took", (end-start), "seconds to boot up.")

			print("Running the test commands now")
			t = test()
			if t == "0xf8":
				result+="failed/"+t
				print("Nothing seemingly failed this run, something went wrong.")
			elif t == "0xb8":
				result+="passed/"+t
				print("Port 2 failed this run, expected failure")
			elif t == "0x78":
				result+="failed/"+t
				print("Port 1 failed this run, unexpected failure")
			else:
				result+="unknown/"+t
				print("Device in unknown state")

			print("Powering off the device now")
			poweroff()
			
			connT.powerOffPort(PSUPorts[1])
			connT.powerOffPort(PSUPorts[0])

			if k%2 == 0:
				sleep(delay:=r.randint(1000,3000)/1000)
				print("Delayed for", delay, "seconds")

		writer.writerow([result])
		log.append(result)

		logCSV.flush()

		if i+1 < reps:
			print("Test", i+1, "completed.")
			print("Powering the PSU Port off and waiting for 120 seconds")
			sleep(125)
			print("Moving on to test",i+2,"\n")
		else:
			print("Test", i+1, "completed. All done. Moving on")
			sleep(125)

		v.write("\nLoop 9 test "+str(i+1)+" starts here.\n")

	logCSV.close()
	return log

def main():
	try:
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

		

		print("The series of tests will begin now. Good luck!!\n")

		print("Loop 9 initiating now")
		log.append(loop9())
		print("\nLoop 9 complete")

		v.write("\n\nEnd of verbose log. All tests completed without any exceptions.\n\n")
		v.flush()
		v.close()

		print("\nAll tests completed. The log is available as log.csv in the same directory as the script.")
		
	except:
		print("")
		traceback.print_exc()
		verbose()
		v.write("\n\nEnd of verbose log. Testing procedure not complete.\n\n")
		v.flush()
		v.close()


if __name__ == '__main__':
	if len(sys.argv) == 4:
		main()

	else:
		help()
