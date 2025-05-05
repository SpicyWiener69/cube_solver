
class Dim2x2:

    SIDE_LEN = 50
    #SLICE_LEN = SIDE_LEN/3

    #EFFECTOR D (DOWN)
    D_LOWER = 0
    D_HOME = 26
    
    D_LAYER = {
        1: 50,
        2: 79,
        }
    #D_lAYER = [ None, 41, 59, 80]
    #D_LAYER_TOP = 41
    #D_LAYER_MID = 59
    #D_LAYER_ALL = 80

    #D_LAYER_TOP =D_HOME +SLICE_LEN * 1
    #D_LAYER_MID =D_HOME +SLICE_LEN * 2        
    #D_LAYER_ALL =D_HOME +SLICE_LEN * 3

    #EFFECTOR C(CLAMPING)
    C_HOME_OFFSET = 10
    C_HOME =SIDE_LEN + C_HOME_OFFSET
    C_CLAMP =SIDE_LEN - 3
    
    #EFFECTOR G (GRIPPER)
    G_OFFSET = 10
    G_HOME = SIDE_LEN + G_OFFSET
    G_GRIP = SIDE_LEN

class Dim3x3:

    SIDE_LEN = 55
    #SLICE_LEN = SIDE_LEN/3

    #EFFECTOR D (DOWN)
    D_LOWER = 0
    D_HOME = 25
    
    D_LAYER = {
        1: 41,
        2: 59,
        3: 80
    }
    
    C_HOME_OFFSET = 10
    C_HOME =SIDE_LEN + C_HOME_OFFSET
    C_CLAMP =SIDE_LEN - 2
    
    #EFFECTOR G (GRIPPER)
    G_OFFSET = 13
    G_HOME = SIDE_LEN + G_OFFSET
    G_GRIP = SIDE_LEN - 1

class Dim4x4:

    SIDE_LEN = 60
    #SLICE_LEN = SIDE_LEN/3

    #EFFECTOR D (DOWN)
    D_LOWER = 0
    D_HOME = 23
    
    D_LAYER = {
        1: 33,
        2: 47,
        3: 62,
        4: 80,
    }
    
    C_HOME_OFFSET = 5
    C_HOME =SIDE_LEN + C_HOME_OFFSET
    C_CLAMP =SIDE_LEN - 2
    
    #EFFECTOR G (GRIPPER)
    G_OFFSET = 10
    G_HOME = SIDE_LEN + G_OFFSET
    G_GRIP = SIDE_LEN - 1


DIM_CLASSES = {2: Dim2x2, 3: Dim3x3, 4: Dim4x4}

VIDEO_ADDRESS = "https://10.42.0.99:8080/video"