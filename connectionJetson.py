from client import *

from threading import Thread
from time import sleep

# ip = '192.168.137.147' #adres odroida

class Connection(Thread):
	def __init__(self, ip, port):
		Thread.__init__(self)
		self.client = Client(ip, port)
		self.flag = self.client.flag		 
		self.dataFrame = []
	def run(self):
		while True:
			self.client.sendData(self.dataFrame)
			sleep(0.1) # na przyklad 1s opoznienia

	def setDataFrame(self, dataFrame):
		self.dataFrame = dataFrame
		
# connFlag = True # flaga -> opuszczanie petli od razu po polaczeniu
# while connFlag:
# 	# Jetson probuje polaczyc sie z odroidem przez ethernet od razu bo zbootowaniu sie Jetsona
# 	connThread = Connection('192.168.137.147')
# 	connFlag = not connThread.flag

#connThread.start() #rozpoczyna wysylanie ramek danych do odroida przez ethernet
