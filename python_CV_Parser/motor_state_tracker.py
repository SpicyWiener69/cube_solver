from icecream import ic
from constants import DIM_CLASSES
from notation_parser import Move, NotationConvertor

def string_to_action_command(user_input_str) -> list[dict[str, int]]:
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
    # if self.debug:
    #     ic(dataclasses_list)
    return dataclasses_list


class MotorStateTracker:
    def __init__(self, cubesize=3, debug=False):
        #all linear magnitudes unit in mm
        self.cubesize = cubesize
        self.Dim = DIM_CLASSES[cubesize]
        self.HOME_STATE = {
         'D': 0,   
         'C': 70,
         'G': 65
        }
        self.motor_state = self.HOME_STATE.copy()
        self.debug = debug

    def cube_alignment_command(self) -> str:
        homing_str = self.home_command()
        alignment = [
            {"operation": 'D', "magnitude": self.Dim.D_LOWER},
            {"operation": 'G', "magnitude": self.Dim.G_HOME},
            {"operation": 'W', "magnitude": 500},
            {"operation": 'D', "magnitude": self.Dim.D_HOME},
            {"operation": 'C', "magnitude": self.Dim.C_CLAMP},
            {"operation": 'W', "magnitude": 500},
            {"operation": 'C', "magnitude": self.Dim.C_HOME},
            {"operation": 'D', "magnitude": self.Dim.D_LOWER},
            {"operation": 'T', "magnitude": 90},
            {"operation": 'W', "magnitude": 1000},
            {"operation": 'D', "magnitude": self.Dim.D_LAYER[self.cubesize]},
            {"operation": 'W', "magnitude": 500},
            {"operation": 'G', "magnitude": self.Dim.G_GRIP},
            {"operation": 'W', "magnitude": 1000},
            {"operation": 'G', "magnitude": self.Dim.G_HOME},
            {"operation": 'W', "magnitude": 500},
            {"operation": 'D', "magnitude": self.Dim.D_LOWER},
            {"operation": 'T', "magnitude": -90}, 
            {"operation": 'G', "magnitude": self.Dim.G_HOME},
            {"operation": 'C', "magnitude": self.Dim.C_HOME},
            {"operation": 'D', "magnitude": self.Dim.D_HOME},
        ]
        motor_commands = self.action_to_motor_command(alignment)
        #self.motor_state = self.HOME_STATE.copy()#?
        return homing_str + motor_commands
    
    def home_command(self) -> str:
        actions = [
            {"operation": 'D', "magnitude": self.HOME_STATE['D']},
            {"operation": 'C', "magnitude": self.HOME_STATE['C']},
            {"operation": 'G', "magnitude": self.HOME_STATE['G']}
        ]
        motor_commands = self.action_to_motor_command(actions)
        
        if self.debug:
            ic(motor_commands)
        
        return motor_commands

    def clamp_command(self) -> str:
        '''
        returns the command that clamps down on the cube along the y axis, depending on cubesize.
        '''

        actions = [
            {"operation": 'C', "magnitude": self.Dim.C_CLAMP},
            {"operation": 'W', "magnitude": 400},
            {"operation": 'C', "magnitude": self.Dim.C_HOME}
        ]
        motor_commands = self.action_to_motor_command(actions)
        return motor_commands

    def dataclass_to_motor_command(self, dataclasses) -> str:
        abs = self._from_move_to_abs(dataclasses)
        relative = self._abs_to_relative(abs)
        motor_commands = self._gear_ratio_conversion(relative)
        return motor_commands
    
    def action_to_motor_command(self, actions):
        relative = self._abs_to_relative(actions)
        motor_commands = self._gear_ratio_conversion(relative)
        return motor_commands

    def _from_move_to_abs(self, dataclasses:list[Move]) ->list[dict[str,str]]:
        abs_states = []

        notation_to_commands = {
            'x': lambda dir, rep, _: [
                                {"operation": 'D', "magnitude": self.Dim.D_HOME},
                                {"operation": 'C', "magnitude": self.Dim.C_CLAMP},
                                {"operation": 'W', "magnitude": 400},
                                {"operation": 'D', "magnitude": 0},
                                {"operation": 'L', "magnitude": (90 * dir * rep)},
                                {"operation": 'D', "magnitude": self.Dim.D_HOME},
                                {"operation": 'C', "magnitude": self.Dim.C_HOME},
                                ],

            'y': lambda dir, rep, _: [
                                {"operation": 'G', "magnitude": self.Dim.G_HOME},
                                {"operation": 'W', "magnitude": 300},
                                {"operation": 'D', "magnitude": self.Dim.D_LAYER[self.cubesize]},
                                {"operation": 'W', "magnitude": 200},
                                {"operation": 'G', "magnitude": self.Dim.G_GRIP},
                                {"operation": 'W', "magnitude": 400},
                                {"operation": 'D', "magnitude": self.Dim.D_HOME},
                                {"operation": 'T', "magnitude": (90 * dir* rep)},
                                {"operation": 'D', "magnitude": self.Dim.D_LAYER[self.cubesize]},
                                {"operation": 'G', "magnitude": self.Dim.G_HOME},
                                {"operation": 'W', "magnitude": 100},
                                {"operation": 'D', "magnitude": self.Dim.D_LOWER},
                                {"operation": 'T', "magnitude": (90 * dir * rep * -1)}, #return to original value.
                                {"operation": 'D', "magnitude": self.Dim.D_HOME}
                                ],   
                                
            'U': lambda dir, rep, depth: [
                                {"operation": 'G', "magnitude": self.Dim.G_HOME},
                                {"operation": 'C', "magnitude": self.Dim.C_HOME},    
                                {"operation": 'W', "magnitude": 200},
                                {"operation": 'D', "magnitude": self.Dim.D_LAYER[depth]},
                                {"operation": 'C', "magnitude": self.Dim.C_CLAMP},
                                {"operation": 'G', "magnitude": self.Dim.G_GRIP},
                                {"operation": 'W', "magnitude": 200},
                                {"operation": 'T', "magnitude": (90 * dir * rep)},
                                {"operation": 'W', "magnitude": 200},
                                {"operation": 'G', "magnitude": self.Dim.G_HOME},
                                {"operation": 'C', "magnitude": self.Dim.C_HOME},
                                {"operation": 'D', "magnitude": 0},
                                {"operation": 'T', "magnitude": (90 * dir * rep * -1)}, 
                                {"operation": 'D', "magnitude": self.Dim.D_HOME},
                                ],

        }
        for notation in dataclasses:
            magnitude = notation_to_commands.get(notation.name)(notation.direction, notation.repetition, notation.depth)
            abs_states.extend(magnitude)
        if self.debug:
            ic(abs_states)
        return abs_states

    def _abs_to_relative(self, operation_abs_commands):
        commands = []
        for command in operation_abs_commands:
            #only linear operations need abs->relative conversions 
            if command["operation"] in ['D', 'C']:  
                relative = command["magnitude"]- self.motor_state[command["operation"]]   
                #update motor_state
                self.motor_state[command["operation"]] = command["magnitude"]              
                command["magnitude"] = relative
                #command.isrelative = True
            commands.append(command)
        if self.debug:
            ic(commands)
        return commands
        

    def _gear_ratio_conversion(self, relative_commands: list) -> str:
        motor_commands = []
        
        ratios = { 
            'W': lambda value: value * 1,
            'L': lambda value: value * 1,
            'T': lambda value: value * 9.875,
            'C': lambda value: value * ((360 / 40) / 2),  # double pulley magnitude
            'D': lambda value: value * (360 / 63),
            'G': lambda value: value * -3.75 + 311.25  # linear transformation for servo motor
        }
        for relative_command in relative_commands:
            motor = relative_command["operation"]
            magnitude = relative_command["magnitude"]
            if self.debug and motor == 'G':
                print(f'G in mm:{magnitude}')
            deg = ratios[motor](magnitude)
            deg_rounded = round(deg)
            motor_commands.append(f"{motor}:{deg_rounded}")
        ret = "; ".join(motor_commands)
        if self.debug:
            
            ic(ret)
        return ret


if __name__ == "__main__":
    
    cubesize = 3
    state_tracker = MotorStateTracker(cubesize=cubesize, debug=True)
    notation_converter = NotationConvertor(cubesize=cubesize, debug=True)
    notations = ["D"]
    dataclasses = notation_converter.to_dataclasses(notations)
    commands = state_tracker.dataclass_to_motor_command(dataclasses)
    print('________________________')
    commands = state_tracker.home_command()
