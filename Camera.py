import cv2
import numpy as np
from Detector import Detector


class Camera:
    # list of centers (x, y) of currently detected objects
    objCenters = []

    # # list contain lists of zones of currently detected objects
    # objZones =  []

    # list of deltas (dx, dy) defining objects displacament from the frame's center
    objCenterDeltas = []

    # path angle delta
    pathAngle = 0

    # list of distance of currently detected objects
    objDistances = []

    # list of camera flags - True -> Stereo , False -> Mono
    cameraFlag = False

    # list of detected objects
    detections = []

    # level of fill screen
    objectsFillLevel = 0

    # frame dimensions (firstly assumed but updated to real ones when capturing the frame)
    frameHeight = 720
    frameWidth = 1280

    captures = []

    def __init__(self):
        self.detector = Detector()

        # capture for both cameras
        capture_front = cv2.VideoCapture(1)
        capture_front.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        capture_front.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        capture_front.set(cv2.CAP_PROP_FPS, 30)

        capture_down = cv2.VideoCapture(2)
        capture_down.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        capture_down.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        capture_down.set(cv2.CAP_PROP_FPS, 30);

        self.captures = [capture_front, capture_down]

        # selection which camera view to process - [front, down]
        self.view_selection = [True, True]

    def __del__(self):
        for capture in self.captures:
            capture.release()

    def process(self):
        detections = [[]] * 2
        frames = [np.array([])] * 2

        # populate detections from both cameras
        for i in range(2):
            if self.view_selection[i]:
                ret, frame = self.captures[i].read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame_resized = cv2.resize(frame_rgb, self.detector.get_network_size(),
                                               interpolation=cv2.INTER_LINEAR)
                    detections[i] = self.detector.detect(frame_resized)
                    frames[i] = self.draw_boxes(detections[i], frame_resized)
                    frames[i] = cv2.cvtColor(frames[i], cv2.COLOR_BGR2RGB)

        self.detections = detections

        return frames

    def update_frame_dimensions(self, frame):
        self.frameHeight = np.size(frame, 0)
        self.frameWidth = np.size(frame, 1)

    def get_frame_center(self):
        xc = int(self.frameWidth / 2)
        yc = int(self.frameHeight / 2)
        return xc, yc

    def get_object_center(self, detection):
        x, y = detection[2][0], detection[2][1]
        return x, y

    def get_object_size(self, detection):
        width, height = detection[2][2], detection[2][3]
        return width, height

    def get_objects_number(self, camera_detections):
        return len(camera_detections)

    def get_objects_centers(self, camera_detections):
        objects_centers = []
        for detection in camera_detections:
            objects_centers.append(self.get_object_center(detection))
        return objects_centers

    # def saveObjectsCenters(self, detections):
    #     objNum = self.get_objects_number(detections)
    #     for detection in detections:
    #         # if place in list 'objCenters' was previously populated
    #         if detections.index(detection) < len(self.objCenters):
    #             # swap values in this place in list
    #             self.objCenters[detections.index(detection)] = self.get_object_center(detection)
    #         else:
    #             self.objCenters.append(self.get_object_center(detection))
    #
    #     # pop all surplus elements
    #     for i in range(objNum, len(self.objCenters)):
    #         self.objCenters.pop(objNum)

    def get_object_vertexes(self, detection):
        x, y = self.get_object_center(detection)
        w, h = self.get_object_size(detection)
        x_min, y_min, x_max, y_max = self.convert_centered_to_topleft(float(x), float(y), float(w), float(h))
        tl = [x_min, y_min]
        tr = [x_max, y_min]
        br = [x_max, y_max]
        bl = [x_min, y_max]
        rect = [tl, tr, br, bl]

        return rect

    def get_objects_vertexes(self, camera_detections):
        objects_vertexes = []
        for detection in camera_detections:
            objects_vertexes.append(self.get_object_vertexes(detection))
        return objects_vertexes

    def get_object_fill(self, detection):
        obj_vertexes_arr = np.array(self.get_object_vertexes(detection), dtype=np.int32)
        im = np.zeros([self.frameHeight, self.frameWidth], dtype=np.uint8)
        cv2.fillPoly(im, [obj_vertexes_arr], 1)
        objects_area = cv2.countNonZero(im)
        frame_area = self.frameHeight * self.frameWidth
        obj_fill_lvl = objects_area / frame_area * 100
        return obj_fill_lvl

    def get_objects_fills(self, camera_detections):
        obj_vertexes_arr = np.array(self.get_objects_vertexes(camera_detections), dtype=np.int32)
        im = np.zeros([self.frameHeight, self.frameWidth], dtype=np.uint8)
        cv2.fillPoly(im, [obj_vertexes_arr], 1)
        objects_area = cv2.countNonZero(im)
        frame_area = self.frameHeight * self.frameWidth
        obj_fill_lvl = objects_area / frame_area * 100
        return obj_fill_lvl

    def convert_centered_to_topleft(self, x, y, w, h):
        x_min = int(round(x - (w / 2)))
        x_max = int(round(x + (w / 2)))
        y_min = int(round(y - (h / 2)))
        y_max = int(round(y + (h / 2)))
        return x_min, y_min, x_max, y_max

    def draw_boxes(self, camera_detections, img):
        for detection in camera_detections:
            x, y = self.get_object_center(detection)
            w, h = self.get_object_size(detection)
            x_min, y_min, x_max, y_max = self.convert_centered_to_topleft(
                float(x), float(y), float(w), float(h))
            tl = (x_min, y_min)
            br = (x_max, y_max)
            cv2.rectangle(img, tl, br, (0, 255, 0), 1)
            cv2.putText(img,
                        str(camera_detections.index(detection)) + ". "
                        " [" + str(round(detection[1] * 100, 2)) + "]",
                        (tl[0], tl[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        [0, 255, 0], 2)
        return img

    def get_object_center_offset(self, detection):
        xc, yc = self.get_frame_center()
        center = self.get_object_center(detection)
        dx = int(xc - center[0])
        dy = int(yc - center[1])
        return [dx, dy]


    def get_objects_centers_offsets(self, detections):
        xc, yc = self.get_frame_center()
        offsets = []
        for camera_detections in detections:
            camera_offsets = []
            for center in self.get_objects_centers(camera_detections):
                dx = int(xc - center[0])
                dy = int(yc - center[1])
                camera_offsets.append([dx, dy])
            offsets.append(camera_offsets)
        return offsets

    def saveObjectsCenterDeltas(self):
        xc, yc = self.get_frame_center()
        self.objCenterDeltas.clear()
        for center in self.objCenters:
            xo = center[0]
            yo = center[1]
            dx = int(xc - xo)
            dy = int(yc - yo)
            objCenterDelta = dx, dy
            self.objCenterDeltas.append(objCenterDelta)

    def get_path_angle(self, frame):
        grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hsvImage = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #dobrać HSV do koloru ścieżki
        lowerColorPath = np.array([55, 0, 0])
        upperColorPath = np.array([90, 255, 255])
        maskPath = cv2.inRange(hsvImage, lowerColorPath, upperColorPath)
        res = cv2.bitwise_and(frame, frame, mask=maskPath)
        gaussBlur = cv2.medianBlur(res,15)
        grayImage = cv2.cvtColor(gaussBlur, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(grayImage, 127, 255, 0)
        kernel = np.ones((5,5), np.uint8)

        imgErosion = cv2.erode(thresh, kernel, iterations=1)
        imgDilation = cv2.dilate(imgErosion, kernel, iterations=5)
        _, contours,_ = cv2.findContours(imgDilation, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
           rect = cv2.minAreaRect(contour)
           angle = rect[2]
           box = cv2.boxPoints(rect)
           angle=int(rect[2])
           if(rect[1][1]>rect[1][0]):
              cv2.line(frame, (int(box[0][0]),int(box[0][1])), (int(box[1][0]),int(box[1][1])), (0,255,0), 2)
              cv2.line(frame, (int(box[2][0]),int(box[2][1])), (int(box[3][0]),int(box[3][1])), (0,255,0), 2)
              angle=90+abs(int(rect[2]))
           if(rect[1][1]<rect[1][0]):   
              cv2.line(frame, (int(box[0][0]),int(box[0][1])), (int(box[3][0]),int(box[3][1])), (0,255,0), 2)
              cv2.line(frame, (int(box[1][0]),int(box[1][1])), (int(box[2][0]),int(box[2][1])), (0,255,0), 2)
              angle=abs(int(rect[2]))
        cv2.imshow('',frame)
        return angle

    # def get_mono_distance(self, detections):
    #     T = np.zeros((3, 1), dtype=np.float64)
    #     R = np.eye(3, dtype=np.float64)
    #     vectorInReal = 0
    #     self.objDistances.clear()
    #     for detection in detections:
    #        x, y, w, h = detection[2][0],\
    #         detection[2][1],\
    #         detection[2][2],\
    #         detection[2][3]
    #        xmin, ymin, xmax, ymax = self.convert_centered_to_topleft(float(x), float(y), float(w), float(h))
    #        #rozpoznane granice ramki
    #        vectorOnCap = np.array([[xmin,ymin],[xmax,ymin],[xmax,ymax],[xmin,ymax]],dtype=np.float32)
    #        #wielkość r2d2 w rzeczywistosci
    #        if(detections.index(detection) == "0"):
    #           vectorInReal = np.array([[0,0,0],[ 1 * 50, 0, 0 ],[ 1 * 50, 1 * 75, 0 ],[ 0, 1 * 75, 0 ]],dtype=np.float32)
    #        #macierz kamery P1
    #        mtxCam = np.array([[907,0,645],[0,905,341.8],[0,0,1]])
    #        #zniekształcenia radialne i tangencjalne
    #        dist = np.array([[0.022,-0.1223,-0.002,0.003]])
    #        #funkcja zwracająca macierz rotacji i translacji kamery wzgledem rozpoznanego obiektu
    #        cv2.solvePnP(vectorInReal, vectorOnCap, mtxCam, dist, R, T)
    #        self.objDistances.append(T[0][0])


    def get_detections(self):
        return self.detections

    # def get_objects_fills_levels(self):
    #     return self.objectsFillLevel

    # def get_camera_flag(self):
    #     return self.cameraFlag

    def get_objects_distances(self, detection):
        # return self.objDistances
        return [10]

    def getObjCenterDeltasXY(self):
        return self.objCenterDeltas

