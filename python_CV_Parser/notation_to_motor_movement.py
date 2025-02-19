from icecream import ic

#Todo:make 3x3 dimesion class


class convertion3x3:
    
    def __init__(self):
        pass
        #self.table = { 'U': 'U','R':'y! x! U x y', 'F': 'x U x', 'D':'u y!', 'L':'y x! U x y','B':'x U'}
       

    def _solution_to_modified(self,solution): 
        table = { 'U': ['U'], 'R': ['y!', 'x!', 'U', 'x', 'y'], 'F': ['x', 'U', 'x!'], 'D': ['u', 'y!'],\
                  'L': ['y', 'x!', 'U', 'x', 'y!'], 'B': ['x!', 'U', 'x'] }
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
            if i >= len(modified) -2:
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
        cleaned = self._delete_duplicate(modified)
        return cleaned


def NotationToEndeffector(notations):
  

    end_effector_instructions = []

    # effectors = ['g','t','l','r','c','d']
    # #pos in abs position
    # initial_pos = [0, 20, 30, 30, 55, 10]

    abs_positions = {'g': 0, 't': 20, 'l': 30, 'r': 30, 'c': 30, 'd': 10}

    #table in abs position    
    move_table = {'x':[('c',40),('l',90),('r',90)],\
                  'U':[('d',30),('l',90),('r',90),('g',40),('t',90)],\
                  'x!':[('d',30),('l',90),('r',90),('g',40),('t',90)]
                  }
    
    for notation in notations:
        if notation not in move_table.keys():
            return -1
        abs_instructions = move_table[notation]
        for abs_instruction in abs_instructions:
            effector = abs_instruction[0]
            abs_position = abs_instruction[1]
           
            relative_position = abs_position - abs_positions[effector]
            relative_instruction = effector,relative_position
            end_effector_instructions.append(relative_instruction)
            abs_positions[effector] = abs_position    #update abs_positions dictionary
            
    return end_effector_instructions

if __name__ == "__main__":

    convertor = convertion3x3()
    solution = ['U','R','F','F','F','B','L','B','B']
    solution = ['F','B','F','F']
    
    ic(solution)

    cleaned_notations = convertor.convert_all(solution) 
    ic(cleaned_notations)

    end_effector_instructions = NotationToEndeffector(cleaned_notations)
    ic(end_effector_instructions)

    

