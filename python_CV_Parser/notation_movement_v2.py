from icecream import ic
from dataclasses import dataclass


class Dimension3x3:


    side_len = 50
    slice_len = 50/3

    #effector d (down)
    d_home = 30
    d_layer_top =d_home +slice_len * 1
    d_layer_mid =d_home +slice_len * 2        
    d_layer_all =d_home +slice_len * 3

    #effector c(clamping)
    c_home_offset = 5
    c_home =side_len + c_home_offset
    c_clamp =side_len
    
    #effector g (gripper)
    g_home =side_len
    g_offset = 5
    g_release =side_len + g_offset

@dataclass
class NotationDataClass:
    #default values
    name:str = "default"
    direction:int = 1
    repetition:int =1

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



def dataclasses_to_effector_movement(dataclasses): #->list[NotationDataClass]

    pass


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

    
    return cleaned_dataclasses

if __name__ == "__main__":
    #notations = ['U',"U'","U'","U","R","R'","D"]
    notations = ["U'","F2","U2","R'","F"]
    dataclasses = notations_to_dataclasses(notations)
    ic(dataclasses)
    modified_dataclasses = notations_to_modified_notations(dataclasses)
    ic(modified_dataclasses)
    cleaned_dataclasses = remove_repetitions(modified_dataclasses)
    ic(cleaned_dataclasses)

