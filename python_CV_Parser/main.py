from api_call import fetchSolution
from notation_to_movement import convert_all

cube_state = 'DLRRFULLDUBFDURDBFBRBLFU'
solution_notation = fetchSolution(cube_state)
movement_command = convert_all(solution_notation)
print(movement_command)