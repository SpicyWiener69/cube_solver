import cv2
import numpy as np
from icecream import ic
import json

from mask_calibration import resize_frame
from constants import VIDEO_ADDRESS

class compareError(Exception):
    pass

def nothing(_):
    pass

def resolve_colors(hsv_dict):
    '''
    input: hsv color of every cubie, starting from U1.
    the order of sides is listed as:  URFDLB 

    {"1": [20, 118, 121], ....}

    output: DRLUUBFBRBLURRLRUBLRDDFDLFUFUFFDBRDUBRUFLLFDDBFLUBLRBD

    a typical 3x3 will look like this:

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
    cubestate_lst = [None] * len(hsv_dict)
    for cubie, hsv in hsv_dict:
        color_code = solve_hsv_color(hsv)
        cubestate_lst[cubie] = color_code

    return ''.join(cubestate_lst)

def solve_hsv_color(hsv) ->str: #TODO:
    # hsv_range = { 'or': ((32,120,120),(36,255,255)),'red':((347,120,120),(13,255,255)) }
    pass

def read_hsv_json() -> dict:
    file_path = "hsv.json" 

    try:
        with open(file_path) as file:
            hsv_dict = json.load(file)
            #convert from strings to tuples
            #hsv_dict = {eval(key): eval(value) for key, value in hsv_dict.items()}
        return hsv_dict
    
    except FileNotFoundError:
        print(f'file not found, creating one with default values at {file_path}')
        hsv_dict = {'U': [[32,120,120],[36,255,255]]}
        dump_hsv_json(hsv_dict)
        return hsv_dict

def dump_hsv_json(hsv_dict):
    with open('hsv.json', "w") as f:
                json.dump(hsv_dict, f)


def refresh_trackbar(windowname, lowerbounds, upperbounds) -> None:

    cv2.createTrackbar('Lower H', windowname, lowerbounds[0], 179, nothing)
    cv2.createTrackbar('Lower S', windowname, lowerbounds[1], 255, nothing)
    cv2.createTrackbar('Lower V', windowname, lowerbounds[2], 255, nothing)
    cv2.createTrackbar('Upper H', windowname, upperbounds[0], 179, nothing)
    cv2.createTrackbar('Upper S', windowname, upperbounds[1], 255, nothing)
    cv2.createTrackbar('Upper V', windowname, upperbounds[2], 255, nothing)


def hsv_color_calibration() -> None:
    windowname = 'tuner'
    cv2.namedWindow(windowname)
    camera = cv2.VideoCapture(VIDEO_ADDRESS)
    color_picker = '0: U \n1: R\n2: F\n '
    color_index_code = {
        0: 'U',
        1: 'R',
        2: 'F',
        3: 'D',
        4: 'L',
        5: 'B',
    }

    # cv2.createTrackbar('Lower H', windowname, 0, 179, nothing)
    # cv2.createTrackbar('Lower S', windowname, 0, 255, nothing)
    # cv2.createTrackbar('Lower V', windowname, 0, 255, nothing)
    # cv2.createTrackbar('Upper H', windowname, 179, 179, nothing)
    # cv2.createTrackbar('Upper S', windowname, 255, 255, nothing)
    # cv2.createTrackbar('Upper V', windowname, 255, 255, nothing)

    cv2.createTrackbar(color_picker, windowname, 0, 5, nothing)
    color_index = cv2.getTrackbarPos(color_picker, windowname)
    color_code = color_index_code[color_index]
    hsv_dict = read_hsv_json()
    lowerbounds, upperbounds = hsv_dict[color_code]
    refresh_trackbar(windowname, lowerbounds, upperbounds)

    ic('press space to save hsv upper and lower values, q to quit without saving')
    while True:
        _, rawframe = camera.read()
        frame = resize_frame(rawframe, scale_percent=30)
        hsv_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        displayer_frame = np.hstack([frame,hsv_frame])
        # Create trackbars for lower and upper HSV bounds
        
        l_h = cv2.getTrackbarPos('Lower H', windowname)
        l_s = cv2.getTrackbarPos('Lower S', windowname)
        l_v = cv2.getTrackbarPos('Lower V', windowname)
        u_h = cv2.getTrackbarPos('Upper H', windowname)
        u_s = cv2.getTrackbarPos('Upper S', windowname)
        u_v = cv2.getTrackbarPos('Upper V', windowname)
        cv2.imshow(windowname, displayer_frame)

        waitKey_ret = cv2.waitKey(1)
        if waitKey_ret == ord(' '):
            ic('saving values to json:')
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


def sanity_check():

    pass



if __name__ == "__main__":
    # ic(circular_compare(10, 170, 20))  # True  (wrap)
    # ic(circular_compare(15, 20, 10) ) # false  (wrap)
    # ic(circular_compare(5, 0, 10))  # True  normal
    # ic(circular_compare(5, 5, 10))  # True  normal
    
    # ic(circular_compare(5, 0, 10))  # True  normal

    read_hsv_json() 
    hsv_color_calibration()



    
