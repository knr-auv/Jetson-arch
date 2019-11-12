from Camera import Camera
import threading
import time
import cv2

import subprocess

#subprocess.call(["cd ~/bin", "sudo jetson_clocks", "sudo nvpmodel -m 0"])

from connectionJetson import Connection


IP_ADDRESS_ODROID = '10.42.0.159'
PORT_ODROID_1 = 8080  # port do wysyłania danych z kamer na odroida
PORT_ODROID_2 = 8181 # port do wysyłania danych z pada na odro

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
        global detections
        while True:
            frames = self.cam.process()
            with detections_lock:
                detections = self.cam.get_detections()
                # print(detections)

            time.sleep(0.01)

            if frames[0].size != 0:
                cv2.imshow('front_cam', frames[0])
            if frames[1].size != 0:
                cv2.imshow('down_cam', frames[1])

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    def get_camera(self):
        return self.cam


class FrameMakerThread(threading.Thread):
    single_data_frame = []
    multi_data_frame = []

    def __init__(self, cam, connection):
        threading.Thread.__init__(self)
        self.cam = cam
        self.connection = connection

        for item in range(0, 5):
            self.single_data_frame.append(None)

    def make_single_frame(self, detection):
        single_data_frame = [[]] * 5
        single_data_frame[0] = self.cam.get_objects_distances(detection)
        single_data_frame[1] = self.cam.get_object_center_offset(detection)[0]  # x
        single_data_frame[2] = self.cam.get_object_center_offset(detection)[1]  # y
        single_data_frame[3] = self.cam.get_object_fill(detection)
        single_data_frame[4] = detection

        self.single_data_frame = single_data_frame

        return single_data_frame

    def make_multi_frame(self, camera_detections):
        multi_data_frame = []
        for detection in camera_detections:
            single_frame = self.make_single_frame(detection)
            multi_data_frame.append(single_frame)
        return multi_data_frame

    def make_multi_camera_frame(self):
        global detections
        multi_cam_frame = []
        for camera_detections in detections:
            multi_cam_frame.append(self.make_multi_frame(camera_detections))
        return multi_cam_frame

    def run(self):
        while True:
            with detections_lock:
                print("multi_camera:")
                # testing and validating results:
                multi_data_frame_local = self.make_multi_camera_frame()
                print(multi_data_frame_local)
                self.connection.setDataFrame(multi_data_frame_local)
            time.sleep(0.1)  # przykładowe opóźnienie
           


connFlag = True # flaga -> opuszczanie pętli od razu po połączeniu
connThread = ''
while connFlag:
    # Jetson próbuje połączyć się z odroidem przez ethernet od razu bo zbootowaniu się Jetsona
    connThread = Connection(IP_ADDRESS_ODROID, PORT_ODROID_1)
    connFlag = not connThread.flag

cameraThread = CameraThread()
cameraThread.start()

frameMaker = FrameMakerThread(cameraThread.get_camera(), connThread)
connThread.start() #rozpoczyna wysyłanie ramek danych do odroida przez ethernet
frameMaker.start()
