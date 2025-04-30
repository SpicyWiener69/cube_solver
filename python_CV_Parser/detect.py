import json
import threading
import time
import warnings

import cv2
import numpy as np
from icecream import ic
import functools

from mask_calibration import resize_frame

#from rubikscolorresolver.solver import resolve_colors
from color_resolver import resolve_colors




def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} took {elapsed_time:.4f} seconds to run")
        return result
    return wrapper


class Detector:
    def __init__(self, cubesize, debug=False, video_address="https://10.42.0.99:8080/video"):
        self.debug = debug
        self.cubelayer = cubesize
        self.rgb_dict = {}
        self.aoi_dict = self._read_json()
        self.detect_count = 0
        self.video_address = video_address
        self.cap = cv2.VideoCapture(self.video_address)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        self.thread = threading.Thread(target=self._update, daemon=True, args=())
        self.thread.start()
        time.sleep(1)
        return self

    @timeit
    def _update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                self.stopped = True
                
                return
              # Do the SLOW read OUTSIDE the lock
            ret, new_frame = self.cap.read()
        
            # Use a short lock only for the assignment
            with self.lock:
                self.ret = ret
                self.frame = new_frame
    @timeit
    def _read_frame(self):
        with self.lock:
            return self.ret, self.frame

    def stop(self):
        self.stopped = True
        if self.cap.isOpened():
            self.cap.release()
        #self.thread.join()
    # def calibrate_mask(self):
    #     mask_calibration.calibrate_mask(self.cubelayer)

    def reset_detection(self):
        self.aoi_dict = self._read_json()
        self.rgb_dict = {}
        self.detect_count = 0

    def _read_json(self) -> dict:
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

    def _calculate_avg_bbox(self, bbox):
        _, raw_frame = self._read_frame()
        frame = resize_frame(raw_frame)
        roi = frame[bbox[0][1]:bbox[1][1], bbox[0][0]:bbox[1][0], :] 
        if self.debug:
            ic(roi)
            
            #convert from BGRA mean to rgb
        bgra_mean = cv2.mean(roi)
        bgr_mean = list(bgra_mean[0:3])
        rgb_mean = self._bgr2rgb(bgr_mean, rounding=True)
        # rgb_mean = [0,0,0]
        # rgb_mean[0], rgb_mean[1], rgb_mean[2] = round(bgr_mean[2]), round(bgr_mean[1]), round(bgr_mean[0])
        return rgb_mean
    
    def _rgb2bgr(self,rgb: list, rounding=False) -> list:
        bgr = [0] * 3
        if rounding:
            bgr[0], bgr[1], bgr[2] = round(rgb[2]), round(rgb[1]), round(rgb[0])
        else:
            bgr[0], bgr[1], bgr[2] = rgb[2], rgb[1], rgb[0]
        return bgr

    def _bgr2rgb(self,bgr: list, rounding=False) -> list:

        rgb = [0] * 3
        if rounding:
            rgb[0], rgb[1], rgb[2] = round(bgr[2]), round(bgr[1]), round(bgr[0])
        else:
            rgb[0], rgb[1], rgb[2] = bgr[2], bgr[1], bgr[0]
        return rgb



    def display_bboxes(self) -> None:
        _, raw_frame = self._read_frame()
        frame = resize_frame(raw_frame)
        for _, bbox in self.aoi_dict.items():
            cv2.rectangle(frame, bbox[0], bbox[1], color=(255, 255, 255), thickness=2)
        
        cv2.imshow('frame',frame)
            # if cv2.waitKey(1) == ord(' '):
            #     break
        cv2.waitKey(1000)
        cv2.destroyWindow('frame')
        
    def detect_face(self) -> None:
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
        
    def solve_color(self) -> str: 
        #cubestate_str = resolve_colors([ "-j", "--rgb", str(self.rgb_dict)])
        cubestate_str = resolve_colors(self.rgb_dict)
        self.reset_detection()
        return cubestate_str 
    
    def draw_face_rgb(self, facestart: int):
        canvas = np.zeros((1000, 1000, 3), dtype=np.uint8)
        interval_x = np.linspace(0, 1000, self.cubelayer + 1, dtype=np.int32)
        interval_y = np.linspace(0, 1000, self.cubelayer + 1, dtype=np.int32)
        cubie_index = facestart
        for i in range(self.cubelayer):
            for j in range(self.cubelayer):
                rgb = self.rgb_dict[cubie_index]
                bgr = self._rgb2bgr(rgb, rounding=False)
                # bgr = [None] * 3
                # bgr[0], bgr[1], bgr[2],  = rgb[2], rgb[1], rgb[0]
                cv2.rectangle(canvas, pt1=(interval_x[j], interval_y[i]), pt2=(interval_x[j+1], interval_y[i+1]),\
                              color=bgr, thickness=-1)
                cubie_index += 1
        cv2.imshow('face', canvas)
        cv2.waitKey(1000)
        cv2.destroyWindow('face')

if __name__ == "__main__":
    detector = Detector(cubesize=3, debug=True)
 #   detector.rgb_dict = {"15": [20, 118, 121], "20": [191, 33, 6], "2": [133, 126, 10], "47": [238, 247, 254], "45": [5, 128, 133], "46": [196, 202, 34], "28": [199, 47, 8], "41": [140, 5, 1], "10": [169, 6, 7], "40": [141, 8, 0], "11": [22, 122, 124], "37": [9, 134, 140], "43": [5, 127, 130], "22": [190, 32, 5], "54": [200, 199, 29], "29": [16, 47, 138], "42": [132, 7, 5], "19": [15, 39, 113], "34": [196, 44, 5], "33": [18, 40, 123], "35": [6, 39, 118], "12": [162, 7, 5], "23": [190, 30, 6], "50": [238, 247, 252], "8": [140, 131, 14], "31": [16, 42, 129], "1": [184, 195, 227], "51": [228, 246, 248], "9": [191, 194, 229], "39": [6, 131, 135], "16": [161, 6, 4], "44": [130, 5, 3], "32": [17, 43, 128], "3": [189, 193, 228], "4": [143, 135, 11], "6": [131, 121, 8], "27": [9, 37, 100], "49": [241, 252, 248], "26": [174, 23, 2], "5": [137, 129, 5], "21": [21, 38, 107], "52": [201, 209, 38], "18": [161, 6, 4], "25": [15, 36, 101], "17": [17, 115, 118], "14": [19, 121, 123], "38": [145, 6, 3], "7": [191, 202, 234], "48": [198, 197, 21], "36": [197, 41, 1], "13": [18, 122, 123], "30": [193, 44, 4], "53": [242, 251, 250], "24": [185, 24, 6]}
  # detector.draw_face_rgb(19)
   # detector.solve_color()
    
    detector.start()
    #aoi_dict = detector._json_to_dict()
    detector.display_bboxes()
    detector.detect_face()
    detector.draw_face_rgb(1)
    # detector.display_bboxes()
    # detector.detect_face()

    # detector.display_bboxes()
    # detector.detect_face()

    # detector.display_bboxes()
    # detector.detect_face()

    # detector.display_bboxes()
    # detector.detect_face()

    # detector.display_bboxes()
    # detector.detect_face()
    
    # ic(detector.rgb_dict)
    # cubestate = detector.solve_color()
    # ic(cubestate)
    # detector.stop()
    # print("ffadfasdf")
    # detector.reset_detection()

