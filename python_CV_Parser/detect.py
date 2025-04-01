import cv2
import json
import numpy as np
from icecream import ic
import warnings
import subprocess
import mask_calibration

class Detector:
    def __init__(self,cubelayer = 3, video_address = "https://10.42.0.99:8080/video"):
        self.cubelayer = cubelayer
        self.rgb_dict = {}
        self.aoi_dict = self._json_to_dict()
        self.detect_count = 0
        self.video_address = video_address
        self.camera = cv2.VideoCapture(self.video_address)

    def calibrate_mask(self):
        mask_calibration.calibrate_mask(self.cubelayer)

    def reset_detection(self):
        self.aoi_dict = self._json_to_dict()
        self.rgb_dict = {}
        self.detect_count = 0

    def _json_to_dict(self)-> dict:
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
        #camera = cv2.VideoCapture(self.video_address)
        ret, frame = self.camera.read()
        roi = frame[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :] 
        if DEBUG:
            ic(roi)
            #convert from BGRA mean to rgb
        bgra_mean = cv2.mean(roi)
        bgr_mean = list(bgra_mean[0:3])
        rgb_mean = [0,0,0]
        rgb_mean[0], rgb_mean[1], rgb_mean[2] = round(bgr_mean[2]), round(bgr_mean[1]), round(bgr_mean[0])
        return rgb_mean
    
    def display_bboxes(self) -> None:  
        while(True):
            ret, frame = self.camera.read()
            for _, bbox in self.aoi_dict.items():
                cv2.rectangle(frame,bbox[0],bbox[1],color=(255,255,255),thickness=2)
            
            cv2.imshow('frame',frame)
            if cv2.waitKey(1) == ord('q'):
                break

        
    def detect_face(self):
        '''
        required return format is specified here:
        https://github.com/dwalton76/rubiks-color-resolver/blob/master/tests/test-data/2x2x2-random-01.txt
        '''
        #rgb_dict = {}
        
        if self.detect_count > 5:
            warnings.warn("detect_face has been called more than 6 times!", UserWarning)
        for key, bbox in self.aoi_dict.items():
            rgb_mean = self._calculate_avg_bbox(bbox)
            tiles_each_face = self.cubelayer * self.cubelayer
            cube_tile_index = key + self.detect_count * tiles_each_face
            self.rgb_dict[cube_tile_index] = rgb_mean
        self.detect_count += 1
        #return self.rgb_dict

    def resolve_color(self,rgb_dict) -> str: #TODO
        str = subprocess.run(['./rubiks-cube-solver.py', '-j', rgb_dict],capture_output=True)
        cubestate_str = str.stdout.decode('utf-8')
        self.reset_detection()
        return cubestate_str
    
if __name__ == "__main__":
    DEBUG = False
    detector = Detector(cubelayer=3)
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
    
    print(detector.rgb_dict)
    
    detector.reset_detection()

