from icecream import ic
from dataclasses import dataclass

#Todo:make 3x3 dimesion class


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


class notationConvertor:
    
    def __init__(self):
        pass
        #self.table = { 'U': 'U','R':'y! x! U x y', 'F': 'x U x', 'D':'u y!', 'L':'y x! U x y','B':'x U'}
       

    def _solution_to_modified(self,solution): 
        table = { 'U': ['U'], "U'":['U!'],
                'R': ['y!', 'x!', 'U', 'x', 'y'], "R'": ['y!', 'x!', 'U!', 'x', 'y'],
                'F': ['x', 'U', 'x!'], "F'": ['x', 'U!', 'x!'],
                'D': ['u', 'y!'], "D'": ["u'", 'y!'],
                'L': ['y', 'x!', 'U', 'x', 'y!'], "L'": ['y', 'x!', "U'", 'x', 'y!'], 
                'B': ['x!', 'U', 'x'], 'B': ['x!', "U'", 'x']
            }
        
        phaseoneList = []
        for item in solution:
            phaseoneList.append(table[item][:]) #deep copies of values           
        ic(phaseoneList)
        return phaseoneList
    
    def _delete_duplicate(self,modified):

        clean = []
        i = 0
        while(1):
            lst1 = modified[i]
            lst2 = modified[i+1]
            if self._is_Notation_reverse(lst1[-1],lst2[0]):   #last element of a list is reverse of the first element of the next
               lst1.pop(-1)
               lst2.pop(0)
            clean.extend(lst1)
            if i >= len(modified) - 2:
                clean.extend(lst2)
                break
            i+=1
        return clean
        
    def _is_Notation_reverse(self,str1,str2):
        if str1[0] == str2[0]:
            if str1[-1] == '!' and str2[-1] != '!':
                return True
            if  str1[-1] != '!' and str2[-1] == '!':
                return True
        return False

    def convert_all(self,solution):
        modified = self._solution_to_modified(solution)
        #cleaned = self._delete_duplicate(modified)
        return modified ###########################
 
#TODO: notation_to_dataclass,notation_dataclass_to_abs_command cleanup

def notation_to_dataclass(notations)->list:
    dataclasses = []
    @dataclass
    class Notation:
        name:str
        direction:int

    for n in notations:
        if n.endswith('!'):
            dataclasses.append(Notation(name = n[0],direction=1))
        else:
            dataclasses.append(Notation(name = n[0],direction=-1))          
    return dataclasses


    
def notation_dataclass_to_abs_command(notation):
    def command_x():
        return [('c', Dimension3x3.c_clamp), ('lr', notation.direction * 90),('c',Dimension3x3.c_home)]

        return f'c {Dimension3x3.c_clamp} ; l {notation.direction * 90} r {notation.direction * 90};'
    
    def command_y():
        return []
    

    def command_U():
        pass


    command_map = {
        'x': command_x(),
        'U': command_U(),
        'y': command_y(),
    }
    return command_map.get(notation.name)
    

def NotationToEndeffector(notation_dataclasses):


    end_effector_instructions = []
    # #pos in abs position
    # initial_pos = [0, 20, 30, 30, 55, 10]

    abs_positions = {'g': 0, 't': 20, 'l': 30, 'r': 30, 'c': 30, 'd': 10}

    #table in abs position    
    # move_table = {'x':[('c',40),('l',90),('r',90)],\
    #               'U':[('d',30),('l',90),('r',90),('g',40),('t',90)],\
    #               'x!':[('d',30),('l',90),('r',90),('g',40),('t',90)]
    #               }
    
    for notation in notation_dataclasses:
        
        abs_instructions = notation_dataclass_to_abs_command(notation)
        for abs_instruction in abs_instructions:
            effector = abs_instruction[0]
            abs_position = abs_instruction[1]
            relative_position = abs_position - abs_positions[effector]
            relative_instruction = effector,relative_position
            end_effector_instructions.append(relative_instruction)
            abs_positions[effector] = abs_position    #update abs_positions dictionary
            
    return end_effector_instructions

if __name__ == "__main__":

    convertor = notationConvertor()
    solution = ['U','R','F','F','F','B','L','B','B']
    solution = ['F','B','F','F']
    
    ic(solution)

    cleaned_notations = convertor.convert_all(solution) 
    ic(cleaned_notations)

    notation_dataclasses = notation_to_dataclass(cleaned_notations)

    # instruction_table = make_notation_to_instruction_table(Dimension3x3)

    end_effector_instructions = NotationToEndeffector(notation_dataclasses)
    ic(end_effector_instructions)

    

