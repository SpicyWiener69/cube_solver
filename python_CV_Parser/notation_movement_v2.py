from icecream import ic
from dataclasses import dataclass,field
#import math


@dataclass
class Dim3x3:

    SIDE_LEN = 53
    #SLICE_LEN = SIDE_LEN/3

    #EFFECTOR D (DOWN)
    D_LOWER = 0
    D_HOME = 25
    D_LAYER_TOP = 41
    D_LAYER_MID = 59
    D_LAYER_ALL = 80

    #D_LAYER_TOP =D_HOME +SLICE_LEN * 1
    #D_LAYER_MID =D_HOME +SLICE_LEN * 2        
    #D_LAYER_ALL =D_HOME +SLICE_LEN * 3

    #EFFECTOR C(CLAMPING)
    C_HOME_OFFSET = 10
    C_HOME =SIDE_LEN + C_HOME_OFFSET
    C_CLAMP =SIDE_LEN
    
    #EFFECTOR G (GRIPPER)
    G_OFFSET = 25
    G_HOME = SIDE_LEN + G_OFFSET
    G_GRIP = SIDE_LEN + 8


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
    #raise error
    return notations

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
        'R':[NotationDataClass(name='x',direction = 1,repetition = 1),NotationDataClass(name='y',direction=1,repetition = 1)],
        'F':[NotationDataClass(name='x',direction = -1,repetition = 1)],
        'D':[NotationDataClass(name='y',direction = 1,repetition = 1)],
        'L':[NotationDataClass(name='x',direction = 1,repetition = 1),NotationDataClass(name='y',direction=-1,repetition = 1)],
        'B':[NotationDataClass(name='x',direction = 1,repetition = 1)]
    }

    for dataclass in dataclasses:
        setup = move_setup_table[dataclass.name]
        revert = move_revert_table[dataclass.name]
        if dataclass.name == 'D':
            core_move = [NotationDataClass(name='u',direction = dataclass.direction,repetition = dataclass.repetition)]
        else:
            core_move = [NotationDataClass(name='U',direction = dataclass.direction,repetition = dataclass.repetition)]  
        
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

#     dataclasses = notations_to_dataclasses(notations)
#     modified_dataclasses = notations_to_modified_notations(dataclasses)
#     cleaned_dataclasses = remove_repetitions(modified_dataclasses)   
def notation_to_clean_dataclasses(notations):
    steps = [verify_notations,notations_to_dataclasses,notations_to_modified_notations,remove_repetitions]
    data = notations
    for step in steps:
        data = step(data)
    if DEBUG:
        ic(data)
    return data

def string_to_action_command(user_input_str) ->list[dict[str,int]]:
    dataclasses_list = []
    # Split the string by ';' and remove any empty tokens
    tokens = [t.strip() for t in user_input_str.split(';') if t.strip()]
    
    for token in tokens:
        # Split the token by ':' and check that we have exactly 2 parts.
        parts = token.split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid token format: '{token}'. Expected format 'operation:magnitude'.")
        
        operation = parts[0].strip()
        magnitude_str = parts[1].strip()
        
        # Validate that the magnitude part can be converted to an integer.
        try:
            magnitude = int(magnitude_str)
        except ValueError:
            raise ValueError(f"Invalid magnitude value in token: '{token}'. magnitude must be an integer.")
        
        dataclasses_list.append({"operation":operation, "magnitude":magnitude})
    if DEBUG:
        ic(dataclasses_list)
    return dataclasses_list




class MotorStateTracker:
    def __init__(self):
        #all linear magnitudes unit in mm
        self.HOME_STATE = {
         'D':0,   
         'C':70,
         'G':65
        }
        self.motor_state = self.HOME_STATE.copy()

    def cube_alignment_command(self) -> str:
        homing_str  = self.home_command()
        alignment = [
            {"operation":'D', "magnitude": Dim3x3.D_LOWER},
            {"operation":'G', "magnitude": Dim3x3.G_HOME},
            {"operation":'W', "magnitude":500},
            {"operation":'D', "magnitude": Dim3x3.D_HOME},
            {"operation":'C', "magnitude": Dim3x3.C_CLAMP},
            {"operation":'W', "magnitude":500},
            {"operation":'C', "magnitude": Dim3x3.C_HOME},
            {"operation":'D', "magnitude": Dim3x3.D_LOWER},
            {"operation":'T', "magnitude": 90},
            {"operation":'W', "magnitude":1000},
            {"operation":'D', "magnitude": Dim3x3.D_LAYER_ALL},
            {"operation":'W', "magnitude":500},
            {"operation":'G', "magnitude": Dim3x3.G_GRIP},
            {"operation":'W', "magnitude":1000},
            {"operation":'G', "magnitude": Dim3x3.G_HOME},
            {"operation":'W', "magnitude":500},
            {"operation":'D', "magnitude": Dim3x3.D_LOWER},
            {"operation":'T', "magnitude": -90}, 
            {"operation":'G', "magnitude": Dim3x3.G_HOME},
            {"operation":'C', "magnitude":Dim3x3.C_HOME},
            {"operation":'D', "magnitude": Dim3x3.D_HOME},
        ]
        motor_commands = self.action_to_motor_command(alignment)
        #self.motor_state = self.HOME_STATE.copy()#?
        return homing_str + motor_commands
    
    def home_command(self) -> str:
        actions = [
        {"operation" :'D', "magnitude" :self.HOME_STATE['D']},
        {"operation" :'C', "magnitude" : self.HOME_STATE['C']},
        {"operation" :'G', "magnitude" : self.HOME_STATE['G']}
        ]
        motor_commands = self.action_to_motor_command(actions)
        
        if DEBUG:
            ic(motor_commands)
        
        return motor_commands

    def dataclass_to_motor_command(self,dataclasses) -> str:
        abs = self._from_dataclass_to_abs(dataclasses)
        relative = self._abs_to_relative(abs)
        motor_commands = self._gear_ratio_conversion(relative)
        return motor_commands
    
    def action_to_motor_command(self,actions):
        relative = self._abs_to_relative(actions)
        motor_commands = self._gear_ratio_conversion(relative)
        return motor_commands

    def _from_dataclass_to_abs(self,dataclasses) ->list[dict[str,str]]:
        abs_states = []

        notation_to_commands = {
            'x':lambda dir,rep: [
                                {"operation":'D', "magnitude": Dim3x3.D_HOME},
                                {"operation":'C', "magnitude": Dim3x3.C_CLAMP},
                                {"operation":'W', "magnitude":500},
                                {"operation":'D', "magnitude": 0},
                                {"operation":'L', "magnitude": (90 * dir * rep)},
                                {"operation":'D', "magnitude": Dim3x3.D_HOME},
                                {"operation":'C', "magnitude":Dim3x3.C_HOME},
                                ],

            'y':lambda dir,rep: [
                                {"operation":'G', "magnitude": Dim3x3.G_HOME},
                                {"operation":'W', "magnitude":300},
                                {"operation":'D', "magnitude": Dim3x3.D_LAYER_ALL},
                                {"operation":'W', "magnitude":300},
                                {"operation":'G', "magnitude": Dim3x3.G_GRIP},
                                {"operation":'W', "magnitude":400},
                                {"operation":'D', "magnitude": Dim3x3.D_HOME},
                                {"operation":'T', "magnitude": (90 * dir* rep)},
                                {"operation":'D', "magnitude": Dim3x3.D_LAYER_ALL},
                                {"operation":'G', "magnitude": Dim3x3.G_HOME},
                                {"operation":'W', "magnitude":300},
                                {"operation":'D', "magnitude": Dim3x3.D_LOWER},
                                {"operation":'T', "magnitude": (90 * dir * rep * -1)}, #return to original value.
                                {"operation":'D', "magnitude": Dim3x3.D_HOME}
                                ],   
                                
            'U':lambda dir,rep: [
                                {"operation":'C', "magnitude": Dim3x3.C_HOME},    
                                {"operation":'D', "magnitude": Dim3x3.D_LAYER_TOP},
                                {"operation":'C', "magnitude": Dim3x3.C_CLAMP},
                                {"operation":'G', "magnitude":Dim3x3.G_GRIP},
                                {"operation":'W', "magnitude":200},
                                {"operation":'T', "magnitude":(90* dir * rep)},
                                {"operation":'W', "magnitude":200},
                                {"operation":'G', "magnitude":Dim3x3.G_HOME},
                                {"operation":'C', "magnitude": Dim3x3.C_HOME},
                                {"operation":'D', "magnitude":0},
                                {"operation":'T', "magnitude":(90 * dir * rep * -1)}, 
                                {"operation":'D', "magnitude":Dim3x3.D_HOME},
                                ],

            'u':lambda dir,rep: [
                                {"operation":'C', "magnitude": Dim3x3.C_HOME},
                                {"operation":'D', "magnitude": Dim3x3.D_LAYER_MID},
                                {"operation":'W', "magnitude":400},
                                {"operation":'C', "magnitude": Dim3x3.C_CLAMP},
                                {"operation":'G', "magnitude":Dim3x3.G_GRIP},
                                {"operation":'W', "magnitude":500},
                                {"operation":'T', "magnitude":(90* dir * rep)},
                                {"operation":'W', "magnitude":500},
                                {"operation":'G', "magnitude":Dim3x3.G_HOME},
                                {"operation":'C', "magnitude": Dim3x3.C_HOME},
                                {"operation":'D', "magnitude":Dim3x3.D_LOWER},
                                {"operation":'T', "magnitude":(90 * dir * rep * -1)}, 
                                {"operation":'D', "magnitude":Dim3x3.D_HOME},
                                ],
        }
        for notation in dataclasses:
            magnitude = notation_to_commands.get(notation.name)(notation.direction, notation.repetition)
            abs_states.extend(magnitude)
        if DEBUG:
            ic(abs_states)
        return abs_states

    def _abs_to_relative(self,operation_abs_commands): #->list[]
        relative_commands = []
        for command in operation_abs_commands:
            #only linear operations need abs->relative conversions 
            if command["operation"] in ['D','C','G']: 
                relative = command["magnitude"]- self.motor_state[command["operation"]]   
                #update motor_state
                self.motor_state[command["operation"]] = command["magnitude"]              
                command["magnitude"] = relative
                #command.isrelative = True
            relative_commands.append(command)
        if DEBUG:
            ic(relative_commands)
        return relative_commands
        

    def _gear_ratio_conversion(self,relative_commands):
        motor_commands = []
        #converted unit: deg
        ratios = { 
            'W':1,
            'L':1,
            'T':9.875,
            'C':(360/(40)) / 2,  # division of 2 for double the magnitude of C motor pulley
            'D':360/(63),
            'G':(-360/46.3) / 2,  #division of 2 ,negative for servo motor direction adjustment
        }
        for relative_command in relative_commands:
        #if relative_command["operation"] != 'W':
            ratio = ratios[relative_command["operation"]]
            motor = relative_command["operation"]
            deg = ratio * relative_command["magnitude"]
            deg_rounded = round(deg)
            motor_commands.append(f"{motor}:{deg_rounded}")
        ret = "; ".join(motor_commands)
        if DEBUG:
            
            ic(ret)
        return ret






# def usr_abs_to_motor_commands(user_input_str):
#     dataclasses = string_to_dataclasses(user_input_str) 
#     relative_commands = convertor.abs_to_relative(dataclasses)
#     motor_commands = convertor.gear_ratio_conversion(relative_commands)
#     return motor_commands



# def notation_to_motor_commands(notations):
#     dataclasses = notations_to_dataclasses(notations)
#     modified_dataclasses = notations_to_modified_notations(dataclasses)
#     cleaned_dataclasses = remove_repetitions(modified_dataclasses)
#     operation_abs_commands = convertor.from_dataclass_to_abs(cleaned_dataclasses)
#     relative_commands = convertor.abs_to_relative(operation_abs_commands)
#     motor_commands = convertor.gear_ratio_conversion(relative_commands)
#     return motor_commands


DEBUG = False
# convertor = operationConverter()

if __name__ == "__main__":
    DEBUG = True
    convertor = MotorStateTracker()
    notations = ['D']
    dataclasses = notation_to_clean_dataclasses(notations)
    commands = convertor.dataclass_to_motor_command(dataclasses)
    commands = convertor.home_command()
