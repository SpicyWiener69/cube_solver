from icecream import ic
from dataclasses import dataclass
from dimension_constants import DIM_CLASSES

@dataclass
class NotationDataClass:
    #default values
    name:str = "default"
    direction:int = 1
    repetition:int = 1
    layerdepth:int = 1
    
class NotationError(Exception):
    pass

class NotationConvertor:
    
    def __init__(self, cubesize = 3, debug = False):
        self.cubesize = cubesize
        self.Dim = DIM_CLASSES[cubesize]
        self.debug = debug
    def _verify_notations(self, notations):
        #TODO:test
        valid_dict = {
            3: [
                "x", "x2", "x'", "y", "y2", "y'",
                "U", "U'", "U2", "L", "L'", "L2", "F", "F'", "F2",
                "R", "R'", "R2", "B", "B'", "B2", "D", "D'", "D2"
            ],
            4: [
                "x","x2", "x'", "y", "y2", "y'",
                "U", "U'", "U2", "Uw", "Uw'", "Uw2", "L", "L'", "L2", "Lw", "Lw'", "Lw2",
                "F", "F'", "F2", "Fw", "Fw'", "Fw2", "R", "R'", "R2", "Rw", "Rw'", "Rw2",
                "B", "B'", "B2", "Bw", "Bw'", "Bw2", "D", "D'", "D2", "Dw", "Dw'", "Dw2"
            ]
        }
        valid_list = valid_dict[self.cubesize]
        for notation in notations:
            if notation not in valid_list:
                
                raise NotationError(f"{notation} notation not valid for cube size: {self.cubesize}")
        return notations

    def _notations_to_dataclasses(self,notations:list): #->list[NotationDataClass]
        dataclasses = []
        for notation in notations:
            length = len(notation)
            instance = NotationDataClass()

            #name detection
            for char in notation:
                if char in ['x', 'y', 'U', 'L', 'F', 'R', 'B', 'D']:
                    instance.name = char
                    break

            #layerdepth evaluation
            if 'w' in notation:
                if (notation[0].isnumeric()):
                    instance.layerdepth = notation[0]
                else:
                    #special case for 4x4, for example, 2Lw2 is noted as Lw2 instead
                    instance.layerdepth = 2 
            else:
                instance.layerdepth = 1

            #direction and rep count
            if notation.endswith('2'):
                instance.direction = 1
                instance.repetition = 2
            elif notation.endswith("'"):
                instance.direction = -1
                instance.repetition = 1
            else:
                instance.direction = 1
                instance.repetition = 1

            dataclasses.append(instance)
            
        if self.debug:
            ic(dataclasses)
        return dataclasses

    def _notations_to_modified_notations(self,dataclasses):
        modified_dataclasses = []
        move_setup_table = {
            'U':[],
            'R':[NotationDataClass(name='y',direction=-1,repetition = 1),NotationDataClass(name='x',direction=-1,repetition = 1)],
            'F':[NotationDataClass(name='x',direction=1,repetition = 1)],
            'D':[],
            'L':[NotationDataClass(name='y',direction=1,repetition = 1),NotationDataClass(name='x',direction=-1,repetition = 1)],
            'B':[NotationDataClass(name='x',direction=-1,repetition = 1)],
            
            
        }

        move_revert_table = {
            'U':[],
            'R':[NotationDataClass(name='x',direction = 1,repetition = 1),NotationDataClass(name='y',direction=1,repetition = 1)],
            'F':[NotationDataClass(name='x',direction = -1,repetition = 1)],
            'D':[NotationDataClass(name='y',direction = 1,repetition = 1)],
            'L':[NotationDataClass(name='x',direction = 1,repetition = 1),NotationDataClass(name='y',direction=-1,repetition = 1)],
            'B':[NotationDataClass(name='x',direction = 1,repetition = 1)],
            
        }

        for dataclass in dataclasses:
            #x and y moves do not need modifications
            if dataclass.name in ['x', 'y']:
                modified_dataclasses.append(dataclass)
            else:
                setup = move_setup_table[dataclass.name]
                revert = move_revert_table[dataclass.name]
                if dataclass.name == 'D':
                    core_move = [NotationDataClass(
                                                name='U',\
                                                direction = dataclass.direction,\
                                                repetition = dataclass.repetition,\
                                                layerdepth = self.cubesize - dataclass.layerdepth #TODO: implmeent layerdepth in motoer_state tracker
                                                )]
                else:
                    core_move = [NotationDataClass(name='U',
                                                direction = dataclass.direction,
                                                repetition = dataclass.repetition,
                                                layerdepth = dataclass.layerdepth
                                                )]  
                
                modified_lst_inst = []
                modified_lst_inst.extend(setup)
                modified_lst_inst.extend(core_move)
                modified_lst_inst.extend(revert)
                modified_dataclasses.extend(modified_lst_inst)
        if self.debug:
            ic(modified_dataclasses)
        return modified_dataclasses


        #fetch two data from a sliding window, compare and remove extras: U <-> U', etc    
    def _remove_repetitions(self, modified_dataclasses):    #->list[NotationDataClass]
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

            
        if self.debug:
            ic(cleaned_dataclasses)
        return cleaned_dataclasses

    #     dataclasses = notations_to_dataclasses(notations)
    #     modified_dataclasses = notations_to_modified_notations(dataclasses)
    #     cleaned_dataclasses = remove_repetitions(modified_dataclasses)   
    def to_dataclasses(self,notations:list):
        steps = [
                self._verify_notations,\
                self._notations_to_dataclasses, \
                self._notations_to_modified_notations,\
                self._remove_repetitions
                 ]
        data = notations
        for step in steps:
            data = step(data)
        if self.debug:
            ic(data)
        return data


if __name__ == "__main__":
    notationconverter = NotationConvertor(cubesize = 3, debug = True)
    notations = ['U','F2','x']
    notationconverter.to_dataclasses(notations)