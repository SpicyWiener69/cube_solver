from icecream import ic


class convertion3x3:
    
    def __init__(self):
        #self.table = { 'U': 'U','R':'y! x! U x y', 'F': 'x U x', 'D':'u y!', 'L':'y x! U x y','B':'x U'}
        self.table = { 'U': ['U'], 'R': ['y!', 'x!', 'U', 'x', 'y'], 'F': ['x', 'U', 'x'], 'D': ['u', 'y!'],\
                       'L': ['y', 'x!', 'U', 'x', 'y'], 'B': ['x', 'U'] }

    def convert(self,SolutionList):
        phaseoneList = []
        for item in SolutionList:
            phaseoneList.append(self.table[item][:]) #deep copies of values           
        ic(phaseoneList)
        cleaned_up_lst = []
        i = 0
        while(1):
            if phaseoneList[i][-1] == phaseoneList[i+1][0]:  #last element of a list is reverse of the first element of the next
               phaseoneList[i].pop(-1)
               phaseoneList[i+1].pop(0)
            cleaned_up_lst.append(phaseoneList[i])
            if i >= len(phaseoneList) -2:
                cleaned_up_lst.append(phaseoneList[i+1])
                break
            i+=1
        ic(cleaned_up_lst)
        
    #todo:    def _is_Notation_reverse(self,str1,str2):
    

        
convertor = convertion3x3()

convertor.convert(['U','R','F','F','F']) 
