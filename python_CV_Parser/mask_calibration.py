import cv2
import numpy as np
from icecream import ic
import json
import math
from dataclasses import dataclass

@dataclass
class Point:
    x:int = 0
    y:int = 0

def calibrate_mask(cubesize) -> None:
    camera = cv2.VideoCapture("https://10.42.0.99:8080/video")
    print('drag mouse to define coordinates')
    while True:
        #top_left, bottom_right = Point(), Point()
        cv2.namedWindow('frame')
        points = [Point(), Point()]
        cv2.setMouseCallback('frame', mouse, points)    
        while True:
            _, rawframe = camera.read()
            frame = resize_frame(rawframe)
            cv2.imshow('frame',frame)
            cv2.waitKey(1)
            top_left, bottom_right = points[0], points[1]
            if top_left.x < bottom_right.x and top_left.y < bottom_right.y:
                break
            #cv2.destroyWindow('frame')
        print('press space to save, q to quit without saving, any other key to continue:')
        # _, rawframe = camera.read()
        # frame = resize_frame(rawframe)
        #top_left, bottom_right = fetch_mouse_coordinates(frame)
        rectangle_side_len_mean = ((bottom_right.x - top_left.x) + (bottom_right.y - top_left.y)) // 2
        aoi_center_list = fetch_pattern_coordinates(top_left, bottom_right, cubesize)
        ic(aoi_center_list)
        mask = np.zeros((frame.shape), dtype = np.uint8)
        aoi_corners_list = []
        for index, coordinate in enumerate(aoi_center_list):
            aoi_side_len = rectangle_side_len_mean // cubesize - 20
            top_left, bottom_right = center_square_to_corners(coordinate, side_len=aoi_side_len) 
            aoi_corners_list.append(((top_left.x, top_left.y), (bottom_right.x, bottom_right.y)))
            frame = cv2.rectangle(frame, pt1=(top_left.x, top_left.y), pt2=(bottom_right.x, bottom_right.y), thickness=-1, color=(255,255,0))
            frame = cv2.putText(frame, str(index), (top_left.x, top_left.y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
        #ic(aoi_corners_list)
        cv2.imshow('frame',frame)
        wait_ret = cv2.waitKey(0)
        if wait_ret == ord(' '):
            print('saving...')
            save_points_json(aoi_corners_list)
            break
        elif wait_ret == ord('q'):
            print('exit without saving...')
            break 
        


def save_points_json(aoi_list) -> None:
    aoi_dict = {}
    for index, corners in enumerate(aoi_list):
        top_left = corners[0]
        bottom_right = corners[1]
        aoi_dict[f'{index+1}'] = f'{top_left}, {bottom_right}'
    layer_count = int(math.sqrt(len(aoi_dict)))

    with open(f'aoi_json/aois{layer_count}.json', "w") as f:
        json.dump(aoi_dict, f)

def center_square_to_corners(coordinate:Point,side_len = 25) -> tuple[tuple]:
    x, y = coordinate.x,coordinate.y
    top_left = Point(x - side_len // 2, y - side_len // 2)
    bottom_right = Point(x + side_len // 2, y + side_len // 2)
    #cv2.rectangle(mask,pt1 = top_left, pt2 = bottom_right, thickness= -1,color = 255)
    return top_left, bottom_right

def fetch_pattern_coordinates(top_left: Point, bottom_right: Point, cubesize) -> list[tuple]:
    coordinates = []
    x_step = (bottom_right.x -  top_left.x) // (cubesize - 1)
    y_step = (bottom_right.y - top_left.y) // (cubesize - 1)  

    #rectangular pattern of spacing x_step along x, y_step along y
    for i in range(cubesize):
        for j in range(cubesize):
            coordinates.append(Point(top_left.x + x_step * j, top_left.y + y_step * i))
    return coordinates
 
def mouse(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDOWN:
        param[0].x, param[0].y = x, y  # First click: Top-left corner
    elif event == cv2.EVENT_LBUTTONUP:
        param[1].x, param[1].y = x, y 
        #param[0] = (x, y)  # Second click: Bottom-right corner
    
def resize_frame(frame,scale_percent = 50) -> np.array:
    '''
    custom resizeing for current computer display;
    adjust values if needed
    '''
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    frame = cv2.resize(frame,(width, height))  
    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    #if ret:
        #return frame
    return frame

if __name__ == '__main__':
    calibrate_mask(cubesize=4)
    