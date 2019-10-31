from Camera import Camera
import threading
import time
import cv2

import subprocess

#subprocess.call(["cd ~/bin", "sudo jetson_clocks", "sudo nvpmodel -m 0"])

from connectionJetson import Connection

detections_lock = threading.Lock()
lock2 = threading.Lock()

detections = []


class CameraThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.cam = Camera()
        cv2.namedWindow('front_cam', cv2.WINDOW_AUTOSIZE)
        cv2.namedWindow('down_cam', cv2.WINDOW_AUTOSIZE)

    def run(self):
        while True:
            frames = self.cam.process()
            with detections_lock:
                detections = self.cam.get_detections()

            time.sleep(0.01)

            if frames[0].size != 0:
                cv2.imshow('front_cam', frames[0])
            if frames[1] != 0:
                cv2.imshow('down_cam', frames[1])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def get_camera(self):
        return self.cam


class FrameMakerThread(threading.Thread):
    singleDataFrame = []
    multiDataFrame = []

    def __init__(self, cam, connection):
        threading.Thread.__init__(self)
        self.cam = cam
        self.connection = connection

        for item in range(0,6):
            self.singleDataFrame.append(None)

    def make_single_frame(self, detection):
            try:
                print('--------------')
                self.singleDataFrame[0] = self.cam.get_objects_distances(detection)
                print(self.cam.get_object_center(detection))
                self.singleDataFrame[1] = self.cam.get_object_center(detection)[0]  # x
                self.singleDataFrame[2] = self.cam.get_object_center(detection)[1]  # y
                self.singleDataFrame[3] = self.cam.get_object_fill()
                self.singleDataFrame[4] = detection
                self.singleDataFrame[5] = False # flaga
                print('--------------')
                return self.singleDataFrame
            except Exception:
                return [[]]

    def make_multi_frame(self, camera_detections):
        self.multiDataFrame.clear()
        for detection in camera_detections:
            self.multiDataFrame.append(self.make_single_frame(detection))
        return self.multiDataFrame

    def make_multi_camera_frame(self):
        multi_cam_frame = []
        for camera_detections in detections:
            multi_cam_frame.append(self.make_multi_frame(camera_detections))

    def run(self):
        while True:
            with detections_lock:
                self.connection.setDataFrame(self.make_multi_camera_frame())
            time.sleep(0.1)  # przykładowe opóźnienie
           


connFlag = True # flaga -> opuszczanie pętli od razu po połączeniu
connThread = ''
while connFlag:
    # Jetson próbuje połączyć się z odroidem przez ethernet od razu bo zbootowaniu się Jetsona
    connThread = Connection('10.42.0.158')
    connFlag = not connThread.flag

cameraThread = CameraThread()
cameraThread.start()

frameMaker = FrameMakerThread(cameraThread.get_camera(), connThread)
connThread.start() #rozpoczyna wysyłanie ramek danych do odroida przez ethernet
frameMaker.start()
