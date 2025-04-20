import json
import threading
import time
import warnings

import cv2
import numpy as np
from icecream import ic

from mask_calibration import resize_frame
from rubikscolorresolver.solver import resolve_colors


class Detector:
    def __init__(self, cubesize, debug = False, video_address = "https://10.42.0.99:8080/video"):
        self.debug = debug
        self.cubelayer = cubesize
        self.rgb_dict = {}
        self.aoi_dict = self._read_json()
        self.detect_count = 0
        self.video_address = video_address
        self.cap = cv2.VideoCapture(self.video_address)
        self.ret, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        threading.Thread(target=self._update, args=()).start()
        time.sleep(1)
        return self

    def _update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                self.stop()
                return
            self.ret, self.frame = self.cap.read()

    def _read_frame(self):
        return self.ret, self.frame

    def stop(self):
        self.stopped = True
        if self.cap.isOpened():
            self.cap.release()

    # def calibrate_mask(self):
    #     mask_calibration.calibrate_mask(self.cubelayer)

    def reset_detection(self):
        self.aoi_dict = self._read_json()
        self.rgb_dict = {}
        self.detect_count = 0

    def _read_json(self)-> dict:
        file_path = f"aoi_json/aois{self.cubelayer}.json" 
        aoi_dict = {}
        try:
            with open(file_path) as file:
                aoi_dict = json.load(file)
                #convert from strings to tuples
                aoi_dict = {eval(key): eval(value) for key, value in aoi_dict.items()}
                return aoi_dict
            
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found")

    def _calculate_avg_bbox(self,bbox):
        _, raw_frame = self._read_frame()
        frame = resize_frame(raw_frame)
        roi = frame[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :] 
        if self.debug:
            ic(roi)
            
            #convert from BGRA mean to rgb
        bgra_mean = cv2.mean(roi)
        bgr_mean = list(bgra_mean[0:3])
        rgb_mean = [0,0,0]
        rgb_mean[0], rgb_mean[1], rgb_mean[2] = round(bgr_mean[2]), round(bgr_mean[1]), round(bgr_mean[0])
        return rgb_mean
    
    def display_bboxes(self) -> None:  
        #while(True):

        _, raw_frame = self._read_frame()
        frame = resize_frame(raw_frame)
        for _, bbox in self.aoi_dict.items():
            cv2.rectangle(frame,bbox[0],bbox[1],color=(255,255,255),thickness=2)
        
        cv2.imshow('frame',frame)
            # if cv2.waitKey(1) == ord(' '):
            #     break
        cv2.waitKey(1000)
        cv2.destroyWindow('frame')
        
    def detect_face(self):
        '''
        required return format for the rubiks color resolver is specified as:
        https://github.com/dwalton76/rubiks-color-resolver/blob/master/tests/test-data/2x2x2-random-01.txt
        '''
        
        if self.detect_count > 5:
            warnings.warn("detect_face has been called more than 6 times!", UserWarning)
        for key, bbox in self.aoi_dict.items():
            rgb_mean = self._calculate_avg_bbox(bbox)
            if self.debug:
                print(f'rgb mean list{rgb_mean}')
            tiles_each_face = self.cubelayer * self.cubelayer
            cube_tile_index = key + self.detect_count * tiles_each_face
            self.rgb_dict[cube_tile_index] = rgb_mean
        self.detect_count += 1
        #return self.rgb_dict

    def solve_color(self) -> str: 
        cubestate_str = resolve_colors([ "-j", "--rgb", str(self.rgb_dict)])
        self.reset_detection()
        return cubestate_str 
    

if __name__ == "__main__":
    detector = Detector(cubesize = 3, debug = True)
    detector.start()
    #aoi_dict = detector._json_to_dict()
    detector.display_bboxes()
    detector.detect_face()
    
    detector.display_bboxes()
    detector.detect_face()

    detector.display_bboxes()
    detector.detect_face()

    detector.display_bboxes()
    detector.detect_face()

    detector.display_bboxes()
    detector.detect_face()

    detector.display_bboxes()
    detector.detect_face()
    
    ic(detector.rgb_dict)
    cubestate = detector.solve_color()
    ic(cubestate)
    detector.stop()
    print("ffadfasdf")
    # detector.reset_detection()

