#this script will lay the foundation for controlling the RPC3/3A power supply
#over telnet

from telnetlib import Telnet
import msvcrt
import time
import sys

class connection:
	tn = Telnet()
	host = str()
	port = int()
	ON = set()
	OFF = set()

def initTelnet(ip:str, port:int):

	try:
		connection.tn.open(ip, port)
		connection.host = ip
		connection.port = port
		setup()
	except OSError:
		print("Connection with the host was not established.")
		print("Please make sure the host is reachable and try again.")

def refresh():
	if connection.host == "" or not connection.port:
		print("Refresh cannot be done without an initialzed connection. Please initiallize the connection using initTelnet.")

	else:
		connection.tn.close()
		try:
			connection.tn.open(connection.host, connection.port)
			setup()
			#print("The connection has been refreshed. Enjoy")
		except OSError:
			print("Connection with the host was not established.")
			print("Please make sure the host is reachable and try again.")

def fix():
	for i in connection.ON:
		powerOnPort(i)
	for i in connection.OFF:
		powerOffPort(i)

def status(rsp):
	rsp = rsp.split('\r')
	start = -1
	for i in range(0, len(rsp)-1, 1):
		if rsp[i] == '\n      1       Outlet 1    1       Off' or rsp[i] == '\n      1       Outlet 1    1       On ':
			start = i
			break

	if len(rsp) > 5:
		for i in range(1, 9, 1):
			st = rsp[start].split(' ')
			if 'On' in st:
				connection.ON.add(i)
				connection.OFF.discard(i)
			else:
				connection.OFF.add(i)
				connection.ON.discard(i)
			start+=1
	elif len(rsp) == 1:
		print("The PSU is not responding. Please power cycle it and press any key to continue the test")
		done = False
		while not done:
			if msvcrt.kbhit():
				refresh()
				connection.tn.write(bytes('1\r', encoding='utf-8'))
				bak = connection.tn.read_very_eager().decode(encoding='utf-8',errors='ignore')
				rsp = bak.split('\r')
				if len(rsp) <= 1:
					done = False
				else:
					done = True
		fix()

def justSend(cmd):
	connection.tn.write(bytes(str(cmd)+'\r', encoding='utf-8'))


def send(cmd):
	connection.tn.write(bytes(str(cmd)+'\r', encoding='utf-8'))
	status(connection.tn.read_until(b"RPC-3>").decode(encoding='utf-8', errors='ignore'))

def setup():
	connection.tn.read_very_eager()
	send(1)

def powerOffPort(port:int):
	if port > 8 or port < 1:
		print("Only power ports through 1 and 8 exist. Selection out of bounds.")
		return

	connection.tn.write(bytes('off ' + str(port) + '\r', encoding='utf-8'))
	justSend("y")

def powerOnPort(port:int):
	if port > 8 or port < 1:
		print("Only power ports through 1 and 8 exist. Selection out of bounds.")
		return

	connection.tn.write(bytes('on ' + str(port) + '\r', encoding='utf-8'))
	justSend("y")

def togglePort(port:int):
	refresh()
	if port > 8 or port < 1:
		print("Only power ports through 1 and 8 exist. Selection out of bounds.")
		return

	if port in connection.OFF:
		connection.OFF.discard(port)
		powerOnPort(port)
		connection.ON.add(port)
	else:
		connection.ON.discard(port)
		powerOffPort(port)
		connection.OFF.add(port)

def cyclePower(port:int):
	refresh()
	if port > 8 or port < 1:
		print("Only power ports through 1 and 8 exist. Selection out of bounds.")
		return
	togglePort(port)
	time.sleep(10)
	togglePort(port)


def stop():
	for i in connection.ON:
		powerOffPort(i)
	connection.tn.close()
	if len(connection.ON) + len(connection.OFF) != 8:
		print("Warning: The number of on and off ports did not add up to 8.")
	connection.OFF.clear()
	connection.ON.clear()


def on1():
	refresh()
	if not 1 in connection.ON:
		powerOnPort(1)
	else:
		print("1 is already on")
def on2():
	refresh()
	if not 2 in connection.ON:
		powerOnPort(2)
	else:
		print("2 is already on")
def on3():
	refresh()
	if not 3 in connection.ON:
		powerOnPort(3)
	else:
		print("3 is already on")
def on4():
	refresh()
	if not 4 in connection.ON:
		powerOnPort(4)
	else:
		print("4 is already on")
def on5():
	refresh()
	if not 5 in connection.ON:
		powerOnPort(5)
	else:
		print("5 is already on")
def on6():
	refresh()
	if not 6 in connection.ON:
		powerOnPort(6)
	else:
		print("6 is already on")
def on7():
	refresh()
	if not 7 in connection.ON:
		powerOnPort(7)
	else:
		print("7 is already on")
def on8():
	refresh()
	if not 8 in connection.ON:
		powerOnPort(8)
	else:
		print("8 is already on")

def off1():
	refresh()
	if not 1 in connection.OFF:
		powerOffPort(1)
	else:
		print("1 is already off")
def off2():
	refresh()
	if not 2 in connection.OFF:
		powerOffPort(2)
	else:
		print("2 is already off")
def off3():
	refresh()
	if not 3 in connection.OFF:
		powerOffPort(3)
	else:
		print("3 is already off")
def off4():
	refresh()
	if not 4 in connection.OFF:
		powerOffPort(4)
	else:
		print("4 is already off")
def off5():
	refresh()
	if not 5 in connection.OFF:
		powerOffPort(5)
	else:
		print("5 is already off")
def off6():
	refresh()
	if not 6 in connection.OFF:
		powerOffPort(6)
	else:
		print("6 is already off")
def off7():
	refresh()
	if not 7 in connection.OFF:
		powerOffPort(7)
	else:
		print("7 is already off")
def off8():
	refresh()
	if not 8 in connection.OFF:
		powerOffPort(8)
	else:
		print("8 is already off")

def help():
	print("The script can be used as follows:(NOT RECOMMENDED)")
	print(sys.argv[0], "<HOST> <PORT>")
	print("HOST:- The ip address of the host; optional, default value of 23 will be used if not provided")
	print("PORT:- The port over which the Telnet connection will be established; can only be a number\n")
	print("Note that rather than standalone usage, this script was designed as a helper script for a reboot controller script.\n\n")
	return

def main():
	host = sys.argv[1]
	try:
		port = int(sys.argv[2])
	except ValueError:
		print("The port can only be a pure number")

	initTelnet(host, port)
	print("The telent connection was successfully established")

	print("The test cycle will run forever unless stopped.")
	print("The power on PSU port 1 will be toggled every 5 seconds")
	try:
		while True:
			print("\nToggling the port now")
			togglePort(3)
			time.sleep(5)
	except:
		print("\nUser requested exit will be honored. Exiting now...")
		stop()
		return

def mainAlt():
	host = sys.argv[1]
	port = 23

	initTelnet(host, port)
	print("The telent connection was successfully established")

	print("The test cycle will run forever unless stopped.")
	print("The power on PSU port 1 will be toggled every 5 seconds")
	try:
		while True:
			print("\nToggling the port now")
			togglePort(3)
			time.sleep(5)
	except KeyboardInterrupt:
		print("\nKeyboard interrupt detected. Exiting now...")
		stop()
		return
	except:
		print("\nProbably a Telnet communication error. Exiting now...")
		stop()
		return


def debug():
	#not implemented yet
	#a function to allow much more granular control of the process
	pass

if __name__ == '__main__':
	if len(sys.argv) == 2:
		mainAlt()
	elif len(sys.argv) >= 3:
		main()
	elif sys.argv[1] == "debug":
		debug()
	else:
		help()
		
