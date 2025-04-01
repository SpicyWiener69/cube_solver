import cv2
import numpy as np
from icecream import ic
import json
import math
# Create a blank image (black)
# width, height = 500, 500
# image = np.zeros((height, width, 3), dtype=np.uint8)

# class mask_saver:
#     def __init__():
def calibrate_mask(cubesize = 3) -> None:
    camera = cv2.VideoCapture("https://10.42.0.99:8080/video")
    image = readFrame(camera)
    top_left, bottom_right = fetch_mouse_coordinates(image)
    aoi_center_list = fetch_pattern_coordinates(top_left, bottom_right, cubesize)
    ic(aoi_center_list)
    mask = np.zeros((image.shape), dtype = np.uint8)
    aoi_corners_list = []
    for coordinate in aoi_center_list:
        top_left, bottom_right = center_square_to_corners(coordinate)
        aoi_corners_list.append((top_left, bottom_right))
        cv2.rectangle(mask, pt1 = top_left, pt2 = bottom_right, thickness= -1, color = 255)
        #cv2.circle(mask,coordinate,radius=10,color = (255,255,255),thickness=-1)
    save_points_json(aoi_corners_list)
    ic(aoi_corners_list)
    cv2.imshow('mask',mask)
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
            coordinates.append((top_left[0] + x_step * i, top_left[1] + y_step * j))
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
 
def readFrame(camera) -> np.array:
    ret, frame = camera.read()
    frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    if ret:
        return frame
    return None

if __name__ == '__main__':
    calibrate_mask()
   

    

