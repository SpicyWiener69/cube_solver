from icecream import ic
from dataclasses import dataclass

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
    isrelative:bool = False
    

def dataclasses_to_effector_abs(dataclasses):
    abs_states = []

    notation_to_commands = {
        'x':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_HOME),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'LR', movement = (90 * dir * rep), isrelative=True),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME)
                            ],

        'y':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_TOP),
                            EffectorMovement(Effector = 'G', movement = Dim3x3.G_GRIP),
                            EffectorMovement(Effector = 'T', movement = 90 * dir, isrelative=True),
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_HOME),
                            EffectorMovement(Effector = 'T', movement = (90 * dir * rep * -1), isrelative=True),
                            EffectorMovement(Effector = 'G', movement = Dim3x3.G_HOME),
                            ],   
                               
        'U':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_TOP),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'LR', movement = 90 * dir * rep, isrelative=True),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME)
                            ],
        'u':lambda dir,rep: [
                            EffectorMovement(Effector = 'D', movement = Dim3x3.D_LAYER_MID),
                            EffectorMovement(Effector = 'C', movement = Dim3x3.C_CLAMP),
                            EffectorMovement(Effector = 'LR', movement = 90 * dir * rep, isrelative=True),
                            EffectorMovement(Effector = 'C', movement =Dim3x3.C_HOME)
                            ],
    }


    for notation in dataclasses:
        movement = notation_to_commands.get(notation.name)(notation.direction, notation.repetition)
        abs_states.extend(movement)
    return abs_states

#note: only linear effectors need abs->relative conversions 
# def effector_abs_to_relative(commands): #->list[NotationDataClass]
    
#     @dataclass
#     class AbsEffectorState:
#         #default position
#         # angles in degrees, distance in mm:
#         D_dis:int = 30
#         C_dis:int = 50
#         G_angle:int = 66
#         R_angle:int = 90



#     abs_effector_state = AbsEffectorState()

#     for command in commands:



if __name__ == "__main__":
    #notations = ['U',"U'","U'","U","R","R'","D"]
    notations = ["U'","F2","U2","R'","F"]
    dataclasses = notations_to_dataclasses(notations)
    ic(dataclasses)
    modified_dataclasses = notations_to_modified_notations(dataclasses)
    ic(modified_dataclasses)
    cleaned_dataclasses = remove_repetitions(modified_dataclasses)
    ic(cleaned_dataclasses,len(cleaned_dataclasses))
    effector_abs = dataclasses_to_effector_abs(cleaned_dataclasses)
    ic(effector_abs,len(effector_abs))

