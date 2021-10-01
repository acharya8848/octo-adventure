#!/usr/bin/python

#STL imports
import re
from telnetlib import Telnet
from time import sleep, time
from serial import Serial, SerialException

#Regular expression
notFound = re.compile(r'^.*Unknown\sCommand.*$')

#Script version
version = '2.1.1'

class TConnection:
	ON = set()
	OFF = set()
	first = False
	state = False
	#Constructor
	def __init__(self,ip="172.24.0.75",port=23):
		self.ip = ip
		self.port = port
		try:
			self.tn = Telnet(ip,port)
			self.first = True
			self.setup()
		except OSError:
			#print("Error while opening the telnet connection. Exiting now")
			exit()
		return

	def close(self):
		while True:
			try:
				self.justSend("exit")
				self.tn.write(bytes('help\n', encoding='ascii'))
			except EOFError:
				#print("Connection closed")
				return True

	#Sends commands over and reads the status of all the ports
	#Be careful with this one as you can get stuck waiting forever
	def send(self,cmd):
		#print(cmd)
		while True:
			try:
				self.tn.read_very_eager()
				self.tn.write(bytes(str(cmd)+'\n', encoding='ascii'))
			except ConnectionResetError:
				#print("ConnectionResetError encountered, resetting the connection now.")
				self.tn.close()
				self.tn.open(self.ip, self.port)
				continue
			self.last = time()
			rsp = self.tn.read_until(b"9258Telnet->").decode(encoding='ascii', errors='ignore')
			if notFound.match(rsp) is None:
				break

		return self.status(rsp)

	#Sends commands over without reading the status of all the ports
	#Exactly same functionality as send() without the risk of getting stuck
	def justSend(self,cmd):
		#print(cmd)
		while True:
			try:
				self.tn.read_very_eager()
				self.tn.write(bytes(str(cmd)+'\n', encoding='ascii'))
			except ConnectionResetError:
				#print("ConnectionResetError encountered, resetting the connection now.")
				self.tn.close()
				self.tn.close()
				self.tn.open(self.ip, self.port)
				continue
			self.last = time()
			rsp = self.tn.read_until(b"9258Telnet->").decode(encoding='ascii', errors='ignore')
			if notFound.match(rsp) is None:
				break

		return True

	def setup(self):
		self.justSend('admin=12345678')
		self.tn.read_until(b"9258Telnet->").decode(encoding='ascii', errors='ignore')
		return self.send("getpower")

	def status(self,rsp):
		# #print(rsp)
		if (matches:=re.search(re.compile(r'\d\s\d\s\d\s\d'), rsp)) is not None:
			matches = matches.group().split(' ')
			# #print(matches)
			if matches[0] == "1":
				self.ON.add(1)
				self.OFF.discard(1)
			else:
				self.OFF.add(1)
				self.ON.discard(1)
			if matches[1] == "1":
				self.ON.add(2)
				self.OFF.discard(2)
			else:
				self.OFF.add(2)
				self.ON.discard(2)
			if matches[2] == "1":
				self.ON.add(3)
				self.OFF.discard(3)
			else:
				self.OFF.add(3)
				self.ON.discard(3)
			if matches[3] == "1":
				self.ON.add(4)
				self.OFF.discard(4)
			else:
				self.OFF.add(4)
				self.ON.discard(4)

			#print(str(self.ON))
			#print(str(self.OFF))
			return True

		return False

	def powerOffPort(self, port:int = 0):
		self.refresh()
		cmd = ""
		if port > 4 or port < 0:
			return False
		elif port == 0:
			cmd = "setpower p6=0000"
		else:
			cmd = "setpower p6="
			for i in range(1,5,1):
				if i == port:
					cmd+='0'
				else:
					if i in self.ON:
						cmd+='1'
					else:
						cmd+='0'
		return self.send(cmd)

	def powerOnPort(self, port:int = 0):
		self.refresh()
		cmd = ""
		if port > 4 or port < 0:
			return False
		elif port == 0:
			cmd = "setpower p6=1111"
		else:
			cmd = "setpower p6="
			for i in range(1,5,1):
				if i == port:
					cmd+='1'
				else:
					if i in self.ON:
						cmd+='1'
					else:
						cmd+='0'
		return self.send(cmd)

	def togglePort(self,port:int=0):
		self.refresh()
		if port in self.ON:
			return self.powerOffPort(port)
		elif port in self.OFF:
			return self.powerOnPort(port)
		elif port == 0:
			if len(self.ON) != 4:
				self.powerOnPort()
			else:
				self.powerOffPort()

	def refresh(self):
		if self.first:
			if time()-self.last < 100:
				return True

			else:
				self.close()
				try:
					self.tn.open(self.ip, self.port)
					return self.setup()
				except OSError:
					return False

	def update(self):
		self.last = time()
		return self.send("getpower")

	def cyclePower(self, port:int, t:float = 10):
		self.refresh()
		if port > 4 or port < 1:
			return False
		self.togglePort(port)
		sleep(t)
		return self.togglePort(port)

	def on1(self):
		self.refresh()
		if not 1 in self.ON:
			return self.powerOnPort(1)
		elif 1 in self.ON:
			return True
		else:
			return False
	def on2(self):
		self.refresh()
		if not 2 in self.ON:
			return self.powerOnPort(2)
		elif 2 in self.ON:
			return True
		else:
			return False
	def on3(self):
		self.refresh()
		if not 3 in self.ON:
			return self.powerOnPort(3)
		elif 3 in self.ON:
			return True
		else:
			return False
	def on4(self):
		self.refresh()
		if not 4 in self.ON:
			return self.powerOnPort(4)
		elif 4 in self.ON:
			return True
		else:
			return False

	def off1(self):
		self.refresh()
		if not 1 in self.OFF:
			return self.powerOffPort(1)
		elif 1 in self.OFF:
			return True
		else:
			return False
	def off2(self):
		self.refresh()
		if not 2 in self.OFF:
			return self.powerOffPort(2)
		elif 2 in self.OFF:
			return True
		else:
			return False
	def off3(self):
		self.refresh()
		if not 3 in self.OFF:
			return self.powerOffPort(3)
		elif 3 in self.OFF:
			return True
		else:
			return False
	def off4(self):
		self.refresh()
		if not 4 in self.OFF:
			return self.powerOffPort(4)
		elif 4 in self.OFF:
			return True
		else:
			return False


cmdPrompt = re.compile(r'^.*@.*$')

class SConnection:
	device = str()
	rate = int()
	def __init__(self,device:str,rate:int=115200,timeout:float=0.5):
		self.device = device
		self.rate = rate
		self.timeout = timeout
		try:
			self.ser = Serial(device,rate,timeout=timeout)
		except SerialException:
			print("The serial port could not be opened. Exiting now")
			exit()
		return

	def justSend(self,cmd):
		self.ser.write(bytes(str(cmd)+"\r", encoding='ascii'))

		return True

	def send(self,cmd):
		self.ser.write(bytes(str(cmd)+"\r", encoding='ascii'))

		return self.readAll()

	def readAll(self):
		read = ""
		string = ""
		b = time()
		while True:
			read = self.ser.readline().decode('ascii', errors='ignore')

			if not cmdPrompt.match(read) is None:
				#string = read+string
				break
			elif  (time()-b) >= self.timeout:
				break

			string+=read

		return string

	def readline(self):
		if self.ser.in_waiting:
			return self.ser.readline().decode('ascii', errors='ignore')
		else:
			return ""

def help():
	print("This script defines classes 'TConnection' and 'SConnection'.")
	print("These classes will embue the importer with the ability to")
	print("interact with the PSU over telnet and any serial device connected.")
	print("Not made to be run standalone from the console. Exiting now...")
	return

if __name__ == '__main__':
	help()