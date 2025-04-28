import cv2
import numpy as np
from icecream import ic
import json
import math


def calibrate_mask(cubesize) -> None:
    while rue:
    camera = cv2.VideoCapture("https://10.42.0.99:8080/video")
    _, rawframe = camera.read()
    frame = resize_frame(rawframe)
    top_left, bottom_right = fetch_mouse_coordinates(frame)
    rectangle_side_len_mean = ((bottom_right[0] - top_left[0]) + (bottom_right[0] - top_left[0])) // 2
    aoi_center_list = fetch_pattern_coordinates(top_left, bottom_right, cubesize)
    ic(aoi_center_list)
    mask = np.zeros((frame.shape), dtype = np.uint8)
    aoi_corners_list = []
    for index, coordinate in enumerate(aoi_center_list):
        aoi_side_len = rectangle_side_len_mean // cubesize - 20
        top_left, bottom_right = center_square_to_corners(coordinate, side_len=aoi_side_len) 
        aoi_corners_list.append((top_left, bottom_right))
        cv2.rectangle(mask, pt1=top_left, pt2=bottom_right, thickness=-1, color=255)
        cv2.putText(mask, str(index), top_left, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
    save_points_json(aoi_corners_list)
    #ic(aoi_corners_list)
    cv2.imshow('window',mask)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def save_points_json(aoi_list) -> None:
    aoi_dict = {}
    for index, corners in enumerate(aoi_list):
        top_left = corners[0]
        bottom_right = corners[1]
        aoi_dict[f'{index+1}'] = f'{top_left}, {bottom_right}'
    layer_count = int(math.sqrt(len(aoi_dict)))

    with open(f'aoi_json/aois{layer_count}.json', "w") as f:
        json.dump(aoi_dict, f)

def center_square_to_corners(coordinate,side_len = 25) -> tuple[tuple]:
    x,y = coordinate[0],coordinate[1]
    top_left = (x - side_len // 2, y - side_len // 2)
    bottom_right = (x + side_len // 2, y + side_len // 2)
    #cv2.rectangle(mask,pt1 = top_left, pt2 = bottom_right, thickness= -1,color = 255)
    return top_left,bottom_right

def fetch_pattern_coordinates(top_left,bottom_right,cubesize) -> list[tuple]:
    coordinates = []
    x_step = (bottom_right[0] -  top_left[0]) // (cubesize - 1)
    y_step = (bottom_right[1] - top_left[1]) // (cubesize - 1)  

    #rectangular pattern of spacing x_step along x, y_step along y
    for i in range(cubesize):
        for j in range(cubesize):
            coordinates.append((top_left[0] + x_step * j, top_left[1] + y_step * i))
    return coordinates

def fetch_mouse_coordinates(image) -> tuple[tuple]:

    def mouse(event,x,y,flags,param):
        nonlocal valid_coordinate
        nonlocal top_left, bottom_right
        if event == cv2.EVENT_LBUTTONDOWN:
            top_left = (x, y)  # First click: Top-left corner
        elif event == cv2.EVENT_LBUTTONUP:
            bottom_right = (x, y)  # Second click: Bottom-right corner
            if top_left[0] < bottom_right[0] and top_left[1] <bottom_right[1]:
                valid_coordinate = True
            else:
                print('invalid coordinates; try again')
    while True:
        top_left = None
        bottom_right = None
        valid_coordinate = False   
        cv2.imshow('image',image)
        cv2.setMouseCallback('image',mouse)    
        while True:
            if  valid_coordinate:
                break
            cv2.waitKey(1)
        copy = image.copy()
        cv2.rectangle(copy,top_left,bottom_right,color=255,thickness=4)
        cv2.imshow('image',copy)
        ret = cv2.waitKey(0)
        if ret == ord('q'):
            cv2.destroyWindow('image')
            break
    return top_left, bottom_right
 

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
    calibrate_mask(cubesize=3)
   

    

