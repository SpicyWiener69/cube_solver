import subprocess
import os

import kociemba
from icecream import ic

from rubikscolorresolver.solver import resolve_colors

def fetch_solution(cube_state):
    #change the cwd due to api path
    original_wd = os.getcwd()
    os.chdir('rubiks-cube-NxNxN-solver')
    string = subprocess.run(['./rubiks-cube-solver.py', '--state', cube_state],capture_output=True)
    #print(str)
    solution_str = string.stdout.decode('utf-8')
    #print(solution_str)
    #TODO: cube is already solved stoping
    solution = solution_str.strip().split(' ')[1:]   # "Solution: U R' F U' F2 R F' U' F\n" -> ['U', "R'", 'F', "U'", 'F2', 'R', "F'", "U'", 'F']
    os.chdir(original_wd)
    return solution


# def fetch_solution(cube_state):
#     string = kociemba.solve(cube_state)
#     return string.split(' ')

if __name__ == "__main__":
    #dummy cases for testing

    # cube_state = 'DLRRFULLDUBFDURDBFBRBLFU'
    # fetch_solution(cube_state)

    # cube_state = 'RRBBUFBFBRLRRRFRDDURUBFBBRFLUDUDFLLFFLLLLDFBDDDUUBDLUU'
    # fetch_solution(cube_state)
    
    cube_state = 'UUUUUUUUURRRRLRRRRFFFFBFFFFDDDDDDDDDLLLLRLLLLBBBBFBBBB'
    ic(fetch_solution(cube_state))



    #cube_state = 'BRBLLLBRDLBBDDRRFUDFUDUDFUDDDRURBBBUUDRLFRDLLFBRFLRFLFFFBRULDRUBUBBLDBFRDLLUBUDDULFLRRFLFUBFUFUR'
    #fetch_solution(cube_state)

    

    