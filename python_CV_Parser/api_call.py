
import subprocess
import os


def fetchSolution(cube_state):
    #change the cwd due to api path
    original_wd = os.getcwd()
    os.chdir('rubiks-cube-NxNxN-solver')
    str = subprocess.run(['./rubiks-cube-solver.py', '--state', cube_state],capture_output=True)
    #print(str)
    solution_str = str.stdout.decode('utf-8')
    print(solution_str)
    solution = solution_str.strip().split(' ')[1:]   # "Solution: U R' F U' F2 R F' U' F\n" -> ['U', "R'", 'F', "U'", 'F2', 'R', "F'", "U'", 'F']
    os.chdir(original_wd)
    return solution

# def resolve_color(rgb_dict):
#     str = subprocess.run(['./rubiks-cube-solver.py', '-j', rgb_dict],capture_output=True)
#     solution_str = str.stdout.decode('utf-8')
    
if __name__ == "__main__":
    #dummy cases for testing

    cube_state = 'DLRRFULLDUBFDURDBFBRBLFU'
    fetchSolution(cube_state)

    cube_state = 'BRBLLLBRDLBBDDRRFUDFUDUDFUDDDRURBBBUUDRLFRDLLFBRFLRFLFFFBRULDRUBUBBLDBFRDLLUBUDDULFLRRFLFUBFUFUR'
    fetchSolution(cube_state)