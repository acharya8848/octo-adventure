#!/usr/bin/python

#STL imports
import sys, os
import io
import time
from difflib import ndiff
from datetime import datetime
import csv

#pypi module imports
import serial as s

#custom imports
from connmanCustom import *

Failed = False
psuPort = 0

#OS Login Credentials
uname = "root"			#the user to login as
pwrd = "silicom123"		#the password for the user account
#I hate pfsense
pfsense = False
#If the machine needs sudo, put set as True, else set it as false
needSudo = False
#How long to wait for the device to boot
limit=90
#What string does the OS show when it has finished booting up and is waiting for user login
loginPrompt = "fc26-min login: "
#What commands to run after the device has booted succesfully?
commands = ["i2cget -y 1 0x74 0 b", "i2cget -y 0 0x74 0 b"]
#The expected results after running the commands
rslt = [
		'0xf8',
		'0xf8'
		]
#At this point, the script has been setup for usage through command line.
#Good luck.


fileName = "result.csv"


check = dict()
for i in range(0, len(commands), 1):
	check[commands[i]] = rslt[i]

#PSU Ports the device is connected to
PSUPorts = list()

def help():
	print("\n\nThe script can be used as follows:")
	print("\n\t",sys.argv[0], " <DEVICE> <BAUDRATE> <REPETITIONS>")
	print("\n\tDEVICE:- COMX for windows, /dev/usbX for linux; replace the 'X' with relevant number")
	print("\tBAUDRATE:- A number representing the rate of communication.")
	print("\tREPETITIONS:- Number of times to run the tests for\n\n")
	print("There are parameters that need to be edited before the script is run. Edit the file before use.")
	return

def readBuffer(port):
	string = ""
	while port.in_waiting:
		read = port.readline().decode('ascii', errors='ignore')
		string+=read

	return string


def login(ser):
	if not pfsense:
		ser.write(bytes(uname+"\r", encoding='ascii'))
		time.sleep(1)
		ser.write(bytes(pwrd+"\r", encoding='ascii'))
		time.sleep(1)
	else:
		ser.write(bytes("8\r", encoding='ascii'))
		time.sleep(2)
		readBuffer(ser)

def setup():
	#this will make sure that the booting device
	#reaches the login prompt
	pass

def reboot(ser):
	if needSudo:
		ser.write(bytes(b"sudo reboot\r"))
		time.sleep(1)
		ser.write(bytes(pwrd+"\r", encoding='ascii'))
	else:
		ser.write(bytes("reboot\r", encoding='ascii'))

def poweroff(ser):
	if needSudo:
		ser.write(bytes(b"sudo poweroff\r"))
		time.sleep(1)
		ser.write(bytes(pwrd+"\r", encoding='ascii'))
	else:
		ser.write(bytes("poweroff\r", encoding='ascii'))

def loop1():
	pass

def loop2():
	pass

def loop3():
	pass

def lpop4():
	pass

def loop5():
	pass

def loop6():
	pass

def loop7():
	pass

def loop8():
	pass

def loop9():
	pass

def loop10():
	pass

def main():
	failed = False
	logFile = open(fileName, "w", newline="")
	log = list()
	PSUPorts.append(int(input("Please enter the first port")))
	PSUPorts.append(int(input("Please enter the second port")))
	try:
		ser = s.Serial(sys.argv[1], int(sys.argv[2]), timeout=1)
		print("The serial port was opened succesfully. Running the test", sys.argv[3],"times now...")
	except ValueError:
		print("The baudrate can only be a pure number.")
		return
	try:
		reps = int(sys.argv[3])
		psuPort = int(sys.argv[4])
	except ValueError:
		print("Number of repetions and PSU port can only be numbers.")
		return

	if psuPort < 1 or psuPort > 8:
		print("The PSU port the device is connected to was out of bounds.")
		print("Please enter the proper port number between 1 and 8")
		return

	print("\nInitializing Telent connection with the PSU....")
	initTelnet("172.24.0.75", 23)
	print("Done")

	print("\nRebooting the machine now.")
	reboot(ser)

	print("\n")
	print("The series of tests will begin now. Good luck!!")

	for i in range(0, reps, 1):
		print("Test", i+1, "starting now...")
		print("Waiting for the device to boot up...")
		start = time.time()
		read = ser.readline().decode('ascii', errors='ignore')
		while read != loginPrompt:
			read = ser.readline().decode('ascii', errors='ignore')

			if (time.time()-start) > limit:
				print("The device has failed to boot within", limit, "seconds. Boot number:", i+1)
				print("Please mannually check if there is something wrong with the device.")
				print("The device output until this point has bee logged and is saved in the file", fileName, ".")
				logFile.write(log)
				logFile.write("\n\n\n------Test incomplete------\n\n\n")
				#cyclePower(psuPort)
				failed = True
				break

		if failed:
			failed = False
			#continue
			break

		end = time.time()

		print("Device took", (end-start), "seconds to boot up.")
		print("Running the test commands now")
		login(ser)
		readBuffer(ser)
		for cmd in commands:
			if (cmd == "lsblk" or cmd == "dmidecode -t 0,1,2,3") and needSudo:
				ser.write(bytes("sudo "+cmd+"\r", encoding='ascii'))
				time.sleep(1)
				ser.write(bytes(pwrd+"\r", encoding='ascii'))
			else:
				ser.write(bytes(cmd+"\r", encoding='ascii'))
			time.sleep(1)
			rslt = readBuffer(ser)
			same = True
			if rslt != check[cmd] and cmd != "free":
				diff = [li for li in ndiff(rslt,check[cmd]) if li[0] != ' ']
				for d in diff:
					if d != '-  ' or d != '+  ' or d != '+\n' or d != '-\n' or d != '+\r' or d != '-\r':
						print(cmd+" return not as expected. Please advise.")
						print("Expected:", check[cmd])
						print("Returned:", rslt)
						log+=("\n"+cmd+" return not as expected. Please advise.\n")
						same = False
						break
			if same:
				print(cmd+" return as expected.")
				log+=("\n"+cmd+" return as expected.\n")
				same = False
			log += rslt

		log+=readBuffer(ser)

		print("The required commands were run. Shutting down the machine now.")
		poweroff(ser)

		#cycle the power in both ports here
		powerOffPort(PSUPorts[0])
		powerOffPort(PSUPorts[1])
		sleep(10)
		powerOnPort(PSUPorts[0])
		powerOnPort(PSUPorts[1])

		log+=("\n\n\ntest " + str(i+1) + " complete\n\n\n")

		print(log,file=logFile)

		log = ""

		if not i+2 > reps:
			print("Test", i+1, "completed. Moving on to test",i+2,"\n")
		else:
			print("Test", i+1, "completed.")

	logFile.write("\n\n\n------Log End------")
	logFile.close()
	print("\nAll tests completed. The log is available as", fileName, "in the same directory as the script.")
	ser.close()

def debug():
	print("Not implemented yet. An interactive function for more granular control. Maybe....")
	return

if __name__ == '__main__':
	if len(sys.argv) < 2:
		help()

	elif sys.argv[1] != "debug":
		main()

	else:
		debug()
	
