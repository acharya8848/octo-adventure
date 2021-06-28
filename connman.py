#!/usr/bin/python

#STL imports
from telnetlib import Telnet
from time import sleep, time
from serial import Serial


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
		except OSError:
			return
		self.first = True
		self.setup()
		return

	#Sends commands over and reads the status of all the ports
	#Be careful with this function as you can get stuck
	def send(self,cmd):
		self.tn.write(bytes(str(cmd)+'\r', encoding='utf-8'))
		self.last = time()
		return self.status(self.tn.read_until(b"RPC-3>").decode(encoding='utf-8', errors='ignore'))

	#Sends commands over without reading the status of all the ports
	def justSend(self,cmd):
		self.tn.write(bytes(str(cmd)+'\r', encoding='utf-8'))
		self.last = time()
		return True

	def setup(self):
		self.tn.read_very_eager()
		return self.send(1)

	def status(self,rsp):
		rsp = rsp.split('\r')
		start = -1
		for i in range(0, len(rsp), 1):
			if rsp[i] == '\n      1       Outlet 1    1       Off' or rsp[i] == '\n      1       Outlet 1    1       On ':
				start = i
				break

		if start != -1:
			for i in range(1, 9, 1):
				st = rsp[start]
				st = st.split(' ')
				if 'On' in st:
					self.ON.add(i)
					self.OFF.discard(i)
				else:
					self.OFF.add(i)
					self.ON.discard(i)
				start = start+1
			self.state = True
			return True
		else:
			self.ON.empty()
			self.OFF.empty()
			self.state = False
			return False

	def powerOffPort(self, port:int = 0):
		self.refresh()
		if port > 8 or port < 0:
			return False
		elif port == 0:
			self.justSend("off")
		else:
			self.justSend("off "+str(port))
		return self.send("y")

	def powerOnPort(self, port:int = 0):
		self.refresh()
		if port > 8 or port < 0:
			return False
		elif port == 0:
			self.justSend("on")
		else:
			self.justSend("on "+str(port))
		return self.send("y")

	def togglePort(self,port:int):
		self.refresh()
		if port in self.OFF:
			return self.powerOnPort(port)
		else:
			return self.powerOffPort(port)

	def refresh(self):
		if time()-self.last < 120:
			return True

		else:
			self.tn.close()
			try:
				self.tn.open(self.ip, self.port)
				return self.setup()
			except OSError:
				return False

	def cyclePower(self, port:int, t:float = 10):
		self.refresh()
		if port > 8 or port < 1:
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
	def on5(self):
		self.refresh()
		if not 5 in self.ON:
			return self.powerOnPort(5)
		elif 5 in self.ON:
			return True
		else:
			return False
	def on6(self):
		self.refresh()
		if not 6 in self.ON:
			return self.powerOnPort(6)
		elif 6 in self.ON:
			return True
		else:
			return False
	def on7(self):
		self.refresh()
		if not 7 in self.ON:
			return self.powerOnPort(7)
		elif 7 in self.ON:
			return True
		else:
			return False
	def on8(self):
		self.refresh()
		if not 8 in self.ON:
			return self.powerOnPort(8)
		elif 8 in self.ON:
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
	def off5(self):
		self.refresh()
		if not 5 in self.OFF:
			return self.powerOffPort(5)
		elif 5 in self.OFF:
			return True
		else:
			return False
	def off6(self):
		self.refresh()
		if not 6 in self.OFF:
			return self.powerOffPort(6)
		elif 6 in self.OFF:
			return True
		else:
			return False
	def off7(self):
		self.refresh()
		if not 7 in self.OFF:
			return self.powerOffPort(7)
		elif 7 in self.OFF:
			return True
		else:
			return False
	def off8(self):
		self.refresh()
		if not 8 in self.OFF:
			return self.powerOffPort(8)
		elif 8 in self.OFF:
			return True
		else:
			return False

class SConnection:
	device = str()
	rate = int()
	def __init__(self,device:str,rate:int=115200,timeout=1):
		self.device = device
		self.rate = rate
		self.ser = Serial(device,rate,timeout)

	def send(self,cmd):
		self.ser.write(bytes(str(cmd)+"\r", encoding='ascii'))
		return self.readAll()

	def readAll(self):
		string = ""
		while self.ser.in_waiting:
			read = self.ser.readline().decode('ascii', errors='ignore')
			string+=read

		return string

def help():
	print("This script defines classes 'TConnection' and 'SConnection'.")
	print("These classes will embue the importer with the ability to")
	print("interact with the PSU over telnet and any serial device connected.")
	print("Not made to be run standalone from the console. Exiting now...")
	return

if __name__ == '__main__':
	help()