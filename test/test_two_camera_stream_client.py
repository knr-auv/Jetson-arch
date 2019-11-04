import cv2
import time
import threading
import logging
import sys
sys.path.append('..')
import stream


class StreamThread(threading.Thread):

    def __init__(self, port, cam):
        threading.Thread.__init__(self)
        self.port = port
        self.cam = cv2.VideoCapture(cam)
        self.cam.set(3, 640)
        self.cam.set(4, 480)
        time.sleep(2)

    def run(self):
        stream_send = stream.StreamClient(port=self.port)
        while True:
            ret, frame = self.cam.read()
            stream_send.send_frame(frame)
        self.cam.release()


logging.basicConfig(level=logging.DEBUG)

camera_stream_nr1 = StreamThread(5050, 0)
camera_stream_nr2 = StreamThread(5051, 1)
logging.debug("OK")

camera_stream_nr1.start()
camera_stream_nr2.start()


