from icecream import ic
from dataclasses import dataclass,field
import math



@dataclass
class Dim3x3:

    SIDE_LEN = 53
    #SLICE_LEN = SIDE_LEN/3

    #EFFECTOR D (DOWN)
    D_HOME = 25
    D_LAYER_TOP = 37
    D_LAYER_MID = 55    
    D_LAYER_ALL = 74

    #D_LAYER_TOP =D_HOME +SLICE_LEN * 1
    #D_LAYER_MID =D_HOME +SLICE_LEN * 2        
    #D_LAYER_ALL =D_HOME +SLICE_LEN * 3

    #EFFECTOR C(CLAMPING)
    C_HOME_OFFSET = 5
    C_HOME =SIDE_LEN + C_HOME_OFFSET
    C_CLAMP =SIDE_LEN
    
    #EFFECTOR G (GRIPPER)
    G_OFFSET = 20
    G_HOME = SIDE_LEN + G_OFFSET
    G_GRIP = SIDE_LEN


@dataclass
class NotationDataClass:
    #default values
    name:str = "default"
    direction:int = 1
    repetition:int = 1

    #printing:
    def __str__(self):
        return f"{self.name}{self.direction}{self.repetition})"
    
class NotationConvertor:
    pass
    
def verify_notations(notations):
    ending = ["'" , "2"]

    return True

def notations_to_dataclasses(notations): #->list[NotationDataClass]
    dataclasses = []
    for notation in notations:
        instance = NotationDataClass()
        length = len(notation)
        instance.name = notation[0]  
        if notation.endswith("'"):  #check for reversals
            instance.direction = -1
        else:
            instance.direction = 1   

        if '2' in notation:        #check for double moves 
            instance.repetition = 2
        else:
            instance.repetition = 1

        dataclasses.append(instance)
    
    if DEBUG:
        ic(dataclasses)
    return dataclasses

def notations_to_modified_notations(dataclasses):
    modified_dataclasses = []
    move_setup_table = {
        'U':[],
        'R':[NotationDataClass(name='y',direction=-1,repetition = 1),NotationDataClass(name='x',direction=-1,repetition = 1)],
        'F':[NotationDataClass(name='x',direction=1,repetition = 1)],
        'D':[],
        'L':[NotationDataClass(name='y',direction=1,repetition = 1),NotationDataClass(name='x',direction=-1,repetition = 1)],
        'B':[NotationDataClass(name='x',direction=-1,repetition = 1)]
        
    }

    move_revert_table = {
        'U':[],
        'R':[NotationDataClass(name='x',direction=1,repetition = 1),NotationDataClass(name='y',direction=1,repetition = 1)],
        'F':[NotationDataClass(name='x',direction=-1,repetition = 1)],
        'D':[NotationDataClass(name='y',direction=-1,repetition = 1)],
        'L':[NotationDataClass(name='x',direction=1,repetition = 1),NotationDataClass(name='y',direction=-1,repetition = 1)],
        'B':[NotationDataClass(name='y',direction=-1,repetition = 1)]
    }

    for dataclass in dataclasses:
        setup = move_setup_table[dataclass.name]
        revert = move_revert_table[dataclass.name]
        if dataclass.name == 'D':
            core_move = [NotationDataClass(name='u',direction=dataclass.direction,repetition=dataclass.repetition)]
        else:
            core_move = [NotationDataClass(name='U',direction=dataclass.direction,repetition=dataclass.repetition)]  
        
        modified_lst_inst = []
        modified_lst_inst.extend(setup)
        modified_lst_inst.extend(core_move)
        modified_lst_inst.extend(revert)
        modified_dataclasses.extend(modified_lst_inst)
    if DEBUG:
        ic(modified_dataclasses)
    return modified_dataclasses


    #fetch two data from a sliding window, compare and remove extras: U <-> U', etc    
def remove_repetitions(modified_dataclasses):    #->list[NotationDataClass]
    cleaned_dataclasses = []
    i = 0
    if len(modified_dataclasses) <= 1:
        cleaned_dataclasses.extend(modified_dataclasses)
    else:
        while i< len(modified_dataclasses) - 1:
            data1 = modified_dataclasses[i]
            data2 = modified_dataclasses[i+1]
            if (data1.name == data2.name) and (data1.direction == data2.direction*-1):
                i+=2
            else:
                cleaned_dataclasses.append(data1)
                i+=1
            if i == len(modified_dataclasses) -1:
                cleaned_dataclasses.append(modified_dataclasses[i])
                break

        
    if DEBUG:
        ic(cleaned_dataclasses)
    return cleaned_dataclasses
    
@dataclass
class EffectorMovement:
    Effector:str
    movement:int
    

def string_to_dataclasses(user_input_str):
    dataclasses_list = []
    # Split the string by ';' and remove any empty tokens
    tokens = [t.strip() for t in user_input_str.split(';') if t.strip()]
    
    for token in tokens:
        # Split the token by ':' and check that we have exactly 2 parts.
        parts = token.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid token format: '{token}'. Expected format 'effector:movement'.")
        
        effector = parts[0].strip()
        movement_str = parts[1].strip()
        
        # Validate that the movement part can be converted to an integer.
        try:
            movement = int(movement_str)
        except ValueError:
            raise ValueError(f"Invalid movement value in token: '{token}'. Movement must be an integer.")
        
        dataclasses_list.append(EffectorMovement(Effector=effector, movement=movement))
    if DEBUG:
        ic(dataclasses_list)
    return dataclasses_list


def dataclasses_to_effector_abs(dataclasses):
    abs_states = []

    notation_to_commands = {
        'x':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_HOME),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'D', movement = 0),
                            EffectorMovement(Effector = 'L', movement = (90 * dir * rep)),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME)
                            ],

        'y':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_TOP),
                            EffectorMovement(Effector = 'G', movement = Dim3x3.G_GRIP),
                            EffectorMovement(Effector = 'T', movement = (90 * dir* rep)),
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_HOME),
                            EffectorMovement(Effector = 'T', movement = (90 * dir * rep * -1)), #return to original value.
                            EffectorMovement(Effector = 'G', movement = Dim3x3.G_HOME),
                            ],   
                               
        'U':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_TOP),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'G', movement= Dim3x3.G_GRIP),
                            EffectorMovement(Effector = 'T', movement= (90* dir * rep)),
                            EffectorMovement(Effector = 'G', movement= Dim3x3.G_HOME),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_HOME),
                            EffectorMovement(Effector = 'D', movement =0),
                            EffectorMovement(Effector = 'T', movement =(90 * dir * rep * -1)), 
                            EffectorMovement(Effector = 'D', movement =Dim3x3.D_HOME),
                            ],

        'u':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_MID),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'L', movement = 90 * dir * rep),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME)
                            ],
    }


    for notation in dataclasses:
        movement = notation_to_commands.get(notation.name)(notation.direction, notation.repetition)
        abs_states.extend(movement)
    if DEBUG:
        ic(abs_states)
    return abs_states

class EffectorConverter:
    def __init__(self):
        #all linear movements unit in mm
        self.HOME_STATE = {
         'D':0,   
         'C':70,
         'G':65
        }
        self.motor_state = self.HOME_STATE.copy()
            
    def abs_to_relative(self,effector_abs_commands): #->list[]
        relative_commands = []
        for command in effector_abs_commands:
            #only linear effectors need abs->relative conversions 
            if command.Effector in ['D','C','G']: #self.Effector in ['L', 'T']:
                relative = command.movement - self.motor_state[command.Effector]   
                #update motor_state
                self.motor_state[command.Effector] = command.movement              
                command.movement = relative
                #command.isrelative = True
            relative_commands.append(command)
        if DEBUG:
            ic(relative_commands)
        return relative_commands
        
    def go_home(self):
        
        diff_D = self.HOME_STATE['D'] - self.motor_state['D'] 
        diff_C = self.HOME_STATE['C'] - self.motor_state['C'] 
        diff_G = self.HOME_STATE['G'] - self.motor_state['G'] 
        
        home_commands = [
        EffectorMovement(Effector = 'D', movement = diff_D),
        EffectorMovement(Effector = 'C', movement = diff_C),
        EffectorMovement(Effector = 'G', movement = diff_G)
        ]
        motor_commands = self.gear_ratio_conversion(home_commands)
        self.motor_state = self.HOME_STATE.copy()
        
        if DEBUG:
            ic(motor_commands)
        
        return motor_commands

    def gear_ratio_conversion(self,relative_commands):
        motor_commands = []
        #converted unit: deg
        ratios = { 
            'L':1,
            'T':9.875,
            'C':(360/(40)) / 2,  # division of 2 for double the movement of C motor pulley
            'D':360/(63),
            'G':(-360/46.3) / 2,  #division of 2 ,negative for servo motor direction adjustment
        }
        for relative_command in relative_commands:
            ratio = ratios[relative_command.Effector]
            motor = relative_command.Effector
            deg = ratio * relative_command.movement
            deg_rounded = round(deg)
            motor_commands.append(f"{motor}:{deg_rounded}")
        ret = "; ".join(motor_commands)
        if DEBUG:
            ic(ret)
        return ret






def usr_abs_to_motor_commands(user_input_str):
    dataclasses = string_to_dataclasses(user_input_str) 
    relative_commands = convertor.abs_to_relative(dataclasses)
    motor_commands = convertor.gear_ratio_conversion(relative_commands)
    return motor_commands


def notation_to_motor_commands(notations):
    dataclasses = notations_to_dataclasses(notations)
    modified_dataclasses = notations_to_modified_notations(dataclasses)
    cleaned_dataclasses = remove_repetitions(modified_dataclasses)
    effector_abs_commands = dataclasses_to_effector_abs(cleaned_dataclasses)
    relative_commands = convertor.abs_to_relative(effector_abs_commands)
    motor_commands = convertor.gear_ratio_conversion(relative_commands)
    return motor_commands

def go_home():
    return convertor.go_home()

DEBUG = False
convertor = EffectorConverter()

if __name__ == "__main__":
    DEBUG = True
    notations = ['U']
    notation_to_motor_commands(notations = notations)
    convertor.go_home()
