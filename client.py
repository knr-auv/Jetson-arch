import socket
import pickle
class Client:
	def __init__(self, ip, port):	#konstruktor tworzy socket oraz laczy i testuje polaczenie z serverem
		self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		msg1 = pickle.dumps('Dupaa')
		print('wszedlem')
		try:
			self.client.connect((ip,port))
			print('polaczony')
			msg1 = self.client.recv(4096)
			print('received?')
			self.flag = True
		except Exception as e:
			msg1 = pickle.dumps('Connection error')
			self.flag = False
		finally:
			print("Connection test: ", pickle.loads(msg1))
	def __del__(self):
		self.client.close()
	
	def receiveData(self): 	#metoda, ktora odpalimy w watku i bedzie odbierac naplywajace dane z severa
		data = self.client.recv(4096)
		return pickle.loads(data)
	
	def sendData(self, data):
		self.client.send(pickle.dumps(data))
