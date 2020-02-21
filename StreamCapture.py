import socket
import cv2
from struct import *
import logging
import time
import numpy as np


class StreamCapture:
    """Klasa Tworzy clienta do odbierania ramek zdjec z symulacji"""
    def __init__(self, port=44209, ip='localhost'):
        """Inicjalizacja socekta """
        self.port = port
        self.ip = ip
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.debug("Socket connect port:{}".format(port))
        self.socket.connect((self.ip, self.port))
        logging.debug("Socket now Connect with port:{}".format(port))
        self.data = b""
        time.sleep(1)

    def release(self):
        self.socket.close()

    """Metdoa zwraca klatke OpenCV uzyskana z Symulacji"""
    def read(self):
        self.data = b""
        self.socket.send(b"\x69")
        confirm = self.socket.recv(1)
        if not(confirm == b"\x69"):
            logging.debug("Message error")
            return False, None
        lenght = self.socket.recv(4)
        lenght = unpack('<I', lenght)[0]
        while not(len(self.data) >= lenght):
            self.data += self.socket.recv(4096)
        self.data = np.fromstring(self.data, np.uint8)
        return True, cv2.imdecode(self.data, cv2.IMREAD_COLOR)