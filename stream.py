import cv2
import socket
import struct
import pickle
import logging


class StreamClient:
    """ Klasa tworzy klienta socketa,
    adress ip to adres serwera na komputerze"""

    def __init__(self, ip='10.42.0.74', port=8485):
        """Inicjalizacja socketa"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.socket.connect((self.ip, self.port))
        self.connection = self.socket.makefile('wb')
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        self.img_counter = 0

    """Metoda pobiera klatke i ja wysyla do serwera"""
    def send_frame(self, frame):
        result, data = cv2.imencode('.jpg', frame, self.encode_param)
        data = pickle.dumps(data, 0)
        size = len(data)
        logging.debug(str("{}: {}".format(self.img_counter, size)))
        self.socket.sendall(struct.pack(">L", size) + data)
        self.img_counter += 1
