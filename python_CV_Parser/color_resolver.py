import json
import math

import cv2
import numpy as np
from icecream import ic

from video_stream_threading import VideoStream
from constants import VIDEO_ADDRESS

class compareError(Exception):
    pass

class hsvrangeError(Exception):
    pass

def nothing(_):
    pass


def resolve_colors(rgb_dict):
    '''
    input: 
    hsv color dictionary of every cubie, starting from U1.
    the order of sides is listed as:  FRBLUD
    {"1": [20, 118, 121], ....}

    output: 
        cubestate in URFDLB form,
        with ordering as: URFDLB 
        DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD

    a 3x3 will look like this:

                |************|
                |*U1**U2**U3*|
                |************|
                |*U4**U5**U6*|
                |************|
                |*U7**U8**U9*|
                |************|
    ************|************|************|************
    *L1**L2**L3*|*F1**F2**F3*|*R1**R2**R3*|*B1**B2**B3*
    ************|************|************|************
    *L4**L5**L6*|*F4**F5**F6*|*R4**R5**R6*|*B4**B5**B6*
    ************|************|************|************
    *L7**L8**L9*|*F7**F8**F9*|*R7**R8**R9*|*B7**B8**B9*
    ************|************|************|************
                |************|
                |*D1**D2**D3*|
                |************|
                |*D4**D5**D6*|
                |************|
                |*D7**D8**D9*|
                |************|
    '''

    rgb_dict = swap_cubie_order(rgb_dict)
    cubestate_lst = [None] * len(rgb_dict)
    hsv_dict = rgb_to_hsv_dict(rgb_dict)
    for cubie, hsv in hsv_dict.items():
        color_code = solve_hsv_color(hsv)
        cubestate_lst[cubie-1] = color_code

    return ''.join(cubestate_lst)

def swap_cubie_order(rgb_dict:dict) -> dict:
    '''
    swaps the cubie ordering from detection(FRBLUD) to kociemba format(URFDLB)
    '''
    cube_size = int(math.sqrt(len(rgb_dict) / 6))
    face_square_count = cube_size**2
    new_pos = {}

    for cubie, rgb in rgb_dict.items():
        # 1 -> face_square_count, Face 'F'
        if cubie <= face_square_count:
            offset = 2
        # Face 'R'
        elif  face_square_count < cubie <=  face_square_count * 2:    
            offset = 0
        # Face 'B'
        elif  face_square_count * 2 < cubie <=  face_square_count * 3:    
            offset = 3
        # Face 'L'
        elif  face_square_count * 3 < cubie <=  face_square_count * 4:    
            offset = 1
        # Face 'U'
        elif  face_square_count * 4 < cubie <=  face_square_count * 5:    
            offset = -4
        # Face 'D'
        elif  face_square_count * 5 < cubie <=  face_square_count * 6:    
            offset = -2
        
        new_pos[cubie + (offset * face_square_count)] = rgb

    return new_pos

def rgb_to_hsv_dict(rgb_dict):
    hsv_dict = {}
    for cubie, rgb in rgb_dict.items():
        hsv = cv2.cvtColor(np.array([[rgb]], dtype = np.uint8),cv2.COLOR_RGB2HSV)[0][0]
        hsv_dict[cubie] = hsv
    return hsv_dict

def solve_hsv_color(hsv) -> str: #TODO:
    hsv_ranges = read_hsv_range_json()
    for color_code, bounds in hsv_ranges.items():
        if circular_inrange_single(hsv, bounds[0], bounds[1]):
            return color_code
    raise hsvrangeError(f'{hsv} hsv color not in range of {hsv_ranges}')
    
def read_hsv_range_json() -> dict:
    file_path = "hsv.json" 

    try:
        with open(file_path) as file:
            hsv_ranges = json.load(file)
            #convert from strings to tuples
            #hsv_dict = {eval(key): eval(value) for key, value in hsv_dict.items()}
        return hsv_ranges
    
    except FileNotFoundError:
        print(f'file not found, creating one with default values at {file_path}')
        hsv_ranges = {
                "U": [[32, 120, 120], [36, 255, 255]], "R": [[0, 120, 120], [30, 255, 255]],\
                "F": [[0, 120, 120], [30, 255, 255]], "D": [[0, 120, 120], [30, 255, 255]], \
                "L": [[0, 120, 120], [30, 255, 255]], "B": [[0, 120, 120], [30, 255, 255]]
                }
        dump_hsv_json(hsv_ranges)
        return hsv_ranges

def dump_hsv_json(hsv_dict):
    with open('hsv.json', "w") as f:
                json.dump(hsv_dict, f)


def init_trackbars(hsv_dict, color_code, windowname) -> None:
    lowerbounds, upperbounds = hsv_dict[color_code]
    cv2.createTrackbar('Lower H', windowname, lowerbounds[0], 179, nothing)
    cv2.createTrackbar('Upper H', windowname, upperbounds[0], 179, nothing)
    cv2.createTrackbar('Lower S', windowname, lowerbounds[1], 255, nothing)
    cv2.createTrackbar('Upper S', windowname, upperbounds[1], 255, nothing)
    cv2.createTrackbar('Lower V', windowname, lowerbounds[2], 255, nothing)
    cv2.createTrackbar('Upper V', windowname, upperbounds[2], 255, nothing)


def refresh_trackbars(hsv_dict, color_code, windowname) -> None:
    lowerbounds, upperbounds = hsv_dict[color_code]
    cv2.setTrackbarPos('Lower H', windowname, lowerbounds[0])
    cv2.setTrackbarPos('Upper H', windowname, upperbounds[0])
    cv2.setTrackbarPos('Lower S', windowname, lowerbounds[1])
    cv2.setTrackbarPos('Upper S', windowname, upperbounds[1])
    cv2.setTrackbarPos('Lower V', windowname, lowerbounds[2])
    cv2.setTrackbarPos('Upper V', windowname, upperbounds[2])


def hsv_color_calibration() -> None:
    windowname = 'tuner'
    cv2.namedWindow(windowname)
    stream = VideoStream().start()
    #camera = cv2.VideoCapture(VIDEO_ADDRESS)
    color_picker = '0: U \n1: R\n2: F\n '
   
    color_index_code = {
        0: 'U',
        1: 'R',
        2: 'F',
        3: 'D',
        4: 'L',
        5: 'B',
    }
    color_picker = '\n'.join(f'{k}: {v}' for k, v in color_index_code.items()) + '\n'

    cv2.createTrackbar(color_picker, windowname, 0, 5, nothing)
    current_color_index = cv2.getTrackbarPos(color_picker, windowname)
    prev_color_index = current_color_index
    color_code = color_index_code[current_color_index]
    hsv_dict = read_hsv_range_json()
    init_trackbars(hsv_dict, color_code, windowname)
    
    ic('press space to save hsv upper and lower values, q to quit without saving')
    while True:
        current_color_index = cv2.getTrackbarPos(color_picker, windowname)

        if prev_color_index != current_color_index:
            #update hsv_dict when another face is picked
            #hsv_dict[color_index_code[prev_color_index]] = [[l_h, l_s, l_v], [u_h, u_s, u_v]]
            ic(color_index_code[prev_color_index])
            ic(hsv_dict)
            color_code = color_index_code[current_color_index]
            refresh_trackbars(hsv_dict, color_code, windowname)
            prev_color_index = current_color_index

        # _, rawframe = camera.read()
        # frame = resize_frame(rawframe, scale_percent=30)
        frame = stream.read_resized_frame(scale_percent=30)
        hsv_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        
        l_h = cv2.getTrackbarPos('Lower H', windowname)
        u_h = cv2.getTrackbarPos('Upper H', windowname)
        l_s = cv2.getTrackbarPos('Lower S', windowname)
        u_s = cv2.getTrackbarPos('Upper S', windowname)
        l_v = cv2.getTrackbarPos('Lower V', windowname)
        u_v = cv2.getTrackbarPos('Upper V', windowname)
        hsv_dict[color_index_code[current_color_index]] = [[l_h, l_s, l_v], [u_h, u_s, u_v]]

        masked = circular_inrange_matrix(hsv_frame,[l_h, l_s, l_v], [u_h, u_s, u_v])
        displayer_frame = np.hstack([frame, hsv_frame, cv2.cvtColor(masked, cv2.COLOR_GRAY2BGR)])
        cv2.imshow(windowname, displayer_frame)

        waitKey_ret = cv2.waitKey(1)
        if waitKey_ret == ord(' '):
            ic('saving values to json:')
            dump_hsv_json(hsv_dict)
            break
        if waitKey_ret == ord('q'):
            ic('exiting without saving...')
            
            break
        

def circular_compare(value, lowerbound, upperbound, endpoints = (0,180)):
    if upperbound == lowerbound:
        raise compareError("upper lower bound error")
    if not (endpoints[0] <= upperbound < endpoints[1]) or not (endpoints[0] <= lowerbound < endpoints[1]):
        raise compareError("bounds must be within endpoints")
    
    if upperbound > lowerbound:
        if upperbound >= value >= lowerbound:
            return True
    else:
        if value > lowerbound or value < upperbound:
            return True

    return False

def circular_inrange_single(value, lowerbounds, upperbounds):
    #values H, S, V need to all be inrange of lower-upper values defined in hsv_dict
    return np.all(circular_inrange_matrix(np.array(value), lowerbounds, upperbounds) == 255)


def circular_inrange_matrix(img, lowerbounds, upperbounds) -> np.array:
    #Hue in normal comparision
    lowerbounds = np.array(lowerbounds, dtype = np.uint8)
    upperbounds = np.array(upperbounds, dtype = np.uint8)
    # for lower, upper in zip(lowerbounds,upperbounds):
    #     if lower == upper:
    #         raise compareError("any element in lower bounds and upper bounds should never be equal")
    if lowerbounds[0] < upperbounds[0]:
        return cv2.inRange(img, lowerbounds, upperbounds)
    
    #Hue in wrap comparision
    elif lowerbounds[0] > upperbounds[0]:
        #[180] + upperbounds[:2] , [0] + lowerbounds[:2]
        part1 = cv2.inRange(img, lowerbounds, np.insert(upperbounds[1:], 0, 180))
        part2 = cv2.inRange(img, np.insert(lowerbounds[1:], 0, 0), upperbounds)
        return cv2.bitwise_or(part1,part2)
    
def sanity_check():

    pass


def test_circular_inrange():
    ic(circular_inrange_single(np.array([3,50,70]), [175, 50, 50], [5, 255, 255]))
    ic(circular_inrange_single(np.array([174,40,70]), [174, 50, 50], [176, 255, 255]))
    ic(circular_inrange_matrix(np.array([3,50,70]), [175, 50, 50], [5, 255, 255]))
    img = cv2.imread("example.jpg")
    img1 = circular_inrange_matrix(img, [10, 50, 50], [170, 255, 255])
    img2 = circular_inrange_matrix(img, [175, 50, 50], [5, 255, 255])
    img3 = circular_inrange_matrix(img3, [175, 50, 50], [5, 255, 255])
    # img = resize_frame(img,20)
    # img1 = resize_frame(img1,20)
    # img2 = resize_frame(img2,20)
    cv2.imshow('original', img)
    cv2.imshow('img1',img1)
    cv2.imshow('img2',img2)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # ic(circular_compare(10, 170, 20))  # True  (wrap)
    # ic(circular_compare(15, 20, 10) ) # false  (wrap)
    # ic(circular_compare(5, 0, 10))  # True  normal
    # ic(circular_compare(5, 5, 10))  # True  normal
    
    # ic(circular_compare(5, 0, 10))  # True  normal
    #test_circular_inrange()
    #ic(swap_cubie_order({ 2: [90, 34, 34], 1: [116, 78, 48], 3: [123, 78, 47], 4: [146, 147, 166], 5: [146, 163, 187], 6: [48, 72, 130], 7: [126, 81, 47], 8: [163, 179, 198], 9: [132, 131, 82], 10: [50, 78, 69], 11: [37, 48, 97], 12: [36, 48, 102], 13: [94, 38, 46], 14: [55, 88, 89], 15: [135, 134, 88], 16: [47, 81, 72], 17: [135, 139, 90], 18: [52, 86, 77], 19: [138, 141, 88], 20: [151, 159, 189], 21: [102, 41, 37], 22: [100, 35, 35], 23: [60, 70, 105], 24: [133, 78, 44]}))
    #ic(resolve_colors({"1": [116, 78, 48], "2": [90, 34, 34], "3": [123, 78, 47], "4": [146, 147, 166], "5": [146, 163, 187], "6": [48, 72, 130], "7": [126, 81, 47], "8": [163, 179, 198], "9": [132, 131, 82], "10": [50, 78, 69], "11": [37, 48, 97], "12": [36, 48, 102], "13": [94, 38, 46], "14": [55, 88, 89], "15": [135, 134, 88], "16": [47, 81, 72], "17": [135, 139, 90], "18": [52, 86, 77], "19": [138, 141, 88], "20": [151, 159, 189], "21": [102, 41, 37], "22": [100, 35, 35], "23": [60, 70, 105], "24": [133, 78, 44]}))

    #solve_hsv_color(np.array([4,40,160]))
            
    #read_hsv_range_json() 
    hsv_color_calibration()



    
