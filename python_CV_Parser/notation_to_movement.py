from icecream import ic
from dataclasses import dataclass,field
import math

@dataclass
class Dim3x3:

    SIDE_LEN = 50
    SLICE_LEN = 50/3

    #EFFECTOR D (DOWN)
    D_HOME = 30
    D_LAYER_TOP =D_HOME +SLICE_LEN * 1
    D_LAYER_MID =D_HOME +SLICE_LEN * 2        
    D_LAYER_ALL =D_HOME +SLICE_LEN * 3

    #EFFECTOR C(CLAMPING)
    C_HOME_OFFSET = 5
    C_HOME =SIDE_LEN + C_HOME_OFFSET
    C_CLAMP =SIDE_LEN
    
    #EFFECTOR G (GRIPPER)
    G_OFFSET = 5
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

    return modified_dataclasses


    #fetch two data from a sliding window, compare and remove extras: U <-> U', etc    
def remove_repetitions(modified_dataclasses):    #->list[NotationDataClass]
    cleaned_dataclasses = []
    i = 0
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

    return cleaned_dataclasses
    # for i in range(len(modified_dataclasses)-1):
    #     data1 = modified_dataclasses[i]
    #     data2 = modified_dataclasses[i+1]
    #     if (data1.name == data2.name) and (data1.direction == data2.direction*-1):
    #         continue
    #     cleaned_dataclasses.append(data1)
    #     if i >= len(modified_dataclasses - 2): 
    #         cleaned_dataclasses.append(data2)


@dataclass
class EffectorMovement:
    Effector:str
    movement:int
    isrelative:bool = field(init = False)
    
    def __post_init__(self):
        if self.Effector in ['LR', 'T']:
            self.isrelative = True
        else:
            self.isrelative = False
        

def dataclasses_to_effector_abs(dataclasses):
    abs_states = []

    notation_to_commands = {
        'x':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_HOME),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'LR', movement = (90 * dir * rep)),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME)
                            ],

        'y':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_TOP),
                            EffectorMovement(Effector = 'G', movement = Dim3x3.G_GRIP),
                            EffectorMovement(Effector = 'T', movement = 90 * dir),
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_HOME),
                            EffectorMovement(Effector = 'T', movement = (90 * dir * rep * -1)),
                            EffectorMovement(Effector = 'G', movement = Dim3x3.G_HOME),
                            ],   
                               
        'U':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_TOP),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'LR', movement = 90 * dir * rep),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME),
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_HOME)
                            ],

        'u':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_MID),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'LR', movement = 90 * dir * rep),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME)
                            ],
    }


    for notation in dataclasses:
        movement = notation_to_commands.get(notation.name)(notation.direction, notation.repetition)
        abs_states.extend(movement)
    return abs_states

#note: only linear effectors need abs->relative conversions 
def effector_abs_to_relative(effector_abs_commands): #->list[]
    #all linear movements, value in mm
    relative_commands = []
    previous_abs_position = {
        'D':10,   
        'C':50,
        'G':50
    }

    for command in effector_abs_commands:
        if not command.isrelative:
            relative = command.movement - previous_abs_position[command.Effector]    #newpos - previous = relative 
            previous_abs_position[command.Effector] = command.movement               #update previous_position
            command.movement = relative
            command.isrelative = True
        relative_commands.append(command)
    return relative_commands


def gear_ratio_conversion(relative_commands):
    motor_commands = []
    #converted unit: deg
    ratios = { 
        'LR':1,
        'T':10,
        'C':360/(2* math.pi * 9),
        'D':360/(2* math.pi * 10),
        'G':360/(2* math.pi * 6),
    }
    for relative_command in relative_commands:
        ratio = ratios[relative_command.Effector]
        motor = relative_command.Effector
        deg = ratio * relative_command.movement
        motor_commands.append(f"{motor}:{deg}")
    ret = "; ".join(motor_commands)
    return ret

def convert_all(notations):
    dataclasses = notations_to_dataclasses(notations)

    modified_dataclasses = notations_to_modified_notations(dataclasses)
     
    cleaned_dataclasses = remove_repetitions(modified_dataclasses)      

    effector_abs_commands = dataclasses_to_effector_abs(cleaned_dataclasses)

    relative_commands = effector_abs_to_relative(effector_abs_commands)
   
    motor_commands = gear_ratio_conversion(relative_commands)

    return motor_commands
   


if __name__ == "__main__":
    #notations = ['U',"U'","U'","U","R","R'","D"]
    notations = ["U'","F2","U2","R'","F"]
    dataclasses = notations_to_dataclasses(notations)
    ic(dataclasses)
    
    modified_dataclasses = notations_to_modified_notations(dataclasses)
    ic(modified_dataclasses)
    
    cleaned_dataclasses = remove_repetitions(modified_dataclasses)
    ic(cleaned_dataclasses,len(cleaned_dataclasses))
           

    effector_abs_commands = dataclasses_to_effector_abs(cleaned_dataclasses)
    ic(effector_abs_commands,len(effector_abs_commands))

    relative_commands = effector_abs_to_relative(effector_abs_commands)
    ic(relative_commands,len(relative_commands))

    motor_commands = gear_ratio_conversion(relative_commands)
    ic(motor_commands)