

import subprocess
import os

def fetchSolution(cube_state):
    #change the cwd due to api path
    original_wd = os.getcwd()
    os.chdir('api')
    str = subprocess.run(['./rubiks-cube-solver.py', '--state', cube_state],capture_output=True)
    #print(str)
    solution_str = str.stdout.decode('utf-8')
    print(solution_str)
    solution = solution_str.strip().split(' ')[1:]   # "Solution: U R' F U' F2 R F' U' F\n" -> ['U', "R'", 'F', "U'", 'F2', 'R', "F'", "U'", 'F']
    os.chdir(original_wd)
    return solution


cube_state = 'DLRRFULLDUBFDURDBFBRBLFU'
fetchSolution(cube_state)