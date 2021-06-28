#!/usr/bin/python

'''
	Authors: Anubhav Acharya, Ramie Katan
	Date created: 06/10/2021
	Date last modified: 06/25/2021
	Python Version: 3.9.5
'''

#STL imports
import sys, os, io, time
from difflib import ndiff
import csv

#custom imports
from connmanCustom import Connection

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

#PSU Ports the device is connected to
PSUPorts = [X,X]

#At this point, the script has been setup for usage through command line.
#Good luck.


fileName = "loop1.csv"


check = dict()
for i in range(0, len(commands), 1):
	check[commands[i]] = rslt[i]

#The variables below this line are set using the command line arguments.
#No need to set them here
reps = int()

def help():
	print("\n\nThe script can be used as follows:")
	print("\n\t",sys.argv[0], " <DEVICE> <BAUDRATE> <REPETITIONS>")
	print("\n\tDEVICE:- COMX for windows, /dev/usbX for linux; replace the 'X' with relevant number")
	print("\tBAUDRATE:- A number representing the rate of communication.")
	print("\tREPETITIONS:- Number of times to run the tests for\n\n")
	print("There are parameters that need to be edited before the script is run. Edit the file before use.")
	return


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

def main():
	failed = False
	file = open(fileName, "w", newline="")
	writer = csv.writer(file)
	log = list()

	if len(PSUPorts) == 0:
		print("Please enter the ports the device is connected to before running the script.")
		print("Exiting now...")
		exit()

	try:
		print("\nInitializing Serial connection with the device....")
		global conS
		conS = SConnection(sys.argv[1], int(sys.argv[2]))
		print("Done. Running the test", reps:=int(sys.argv[3]), "times.")
	except SerialError:
		print("A serial connection with the selected device could not be established.")
		exit()
	except ValueError:
		print("Baudrate and reps can only be integers.")
		exit()

	

	for p in PSUPorts:
		if p < 1 or psuPort > 8:
			print("The PSU port the device is connected to was out of bounds.")
			print("Please enter the proper port number between 1 and 8")
			exit()
		conT.powerOnPort(p)

	

	for p in PSUPorts:


if __name__ == '__main__':
	if len(sys.argv) == 4:
		main()

	else:
		help()