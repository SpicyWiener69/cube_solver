# import serial
# from notation_movement_v2 import notation_to_motor_commands,usr_abs_to_motor_commands

# mode = ''

# port = serial.Serial(port = '/dev/ttyACM0', baudrate = 57600,timeout=3)

# while True:
#     picker = input("mode selection(n for Notation control, r for Raw motor control, i for Inverse kinematics):")
#     if picker == 'n':
#         mode = 'Notation'
#     elif picker == 'r':
#         mode = 'raw'
#     elif picker == 'i':
#         mode = 'inverse'

#     if mode == 'Notation':
#         while True:
#             raw_notation = input("input notation:")
#             if raw_notation == '=':   #session end
#                 break
#             raw_notation = raw_notation.split(' ')
            
#             command_str = notation_to_motor_commands(raw_notation)
#             command_str+='#' #command end 
#             print(command_str)
#             port.write(command_str.encode('ascii'))
#             print(port.read_until(expected=b'#'))

#     elif mode == 'raw':
#         while True:
#             raw_command = input("input command:") 
#             if raw_command == '=':
#                 break
#             port.write(raw_command.encode('ascii'))
#             print(port.read_until(expected=b'#'))
    
#     elif mode == 'inverse':
#         while True:
#             str = input("input kinematics:") 
#             if str == '=':
#                 break
#             command_str = usr_abs_to_motor_commands(str)
#             command_str+='#' #command end 
#             port.write(command_str.encode('ascii'))
#             print(port.read_until(expected=b'#'))


import serial
from notation_movement_v2 import notation_to_clean_dataclasses, string_to_action_command, MotorStateTracker
from detect import Detector

class RobotController:
    def __init__(self, port_name='/dev/ttyACM0', baudrate=57600, timeout=3):
        """Initialize the serial connection and mode selection."""
        self.motor_state_tracker = MotorStateTracker()
        self.port = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
        self.modes = {
            's':self.scanner_mode,
            'n': self.notation_mode,
            'r': self.raw_mode,
            'i': self.inverse_kinematics_mode
        }

    def send_command(self, command):
        command += '#'  # Append command end character
        print(f'sent:{command}')
        self.port.write(command.encode('ascii'))
        response = self.port.read_until(expected=b'#')
        print(f"response:{response.decode('ascii')}")

    def scanner_mode(self):
        cubesize  = int(input("Input cube_layer (or '=' to exit): "))
        detector = Detector(cubelayer=cubesize)
        #TODO: implement a function to turn the cube to scan. implement from notations conversion: x, y

    def notation_mode(self):
        while True:
            input_str = input("Input notation (or '=' to exit): ")
            if input_str == '=':
                break
            elif input_str == 'home':
                command = self.motor_state_tracker.home_command()
                self.send_command(command)
            elif input_str == 'align':
                command = self.motor_state_tracker.cube_alignment_command()
                self.send_command(command)
            else:
                dataclasses = notation_to_clean_dataclasses(input_str.split())
                command = self.motor_state_tracker.dataclass_to_motor_command(dataclasses)
                self.send_command(command)

    def inverse_kinematics_mode(self):
        while True:
            kinematics_input = input("Input kinematics (or '=' to exit): ")
            if kinematics_input == '=':

                break
            elif kinematics_input == 'home':
                command_str = self.motor_state_tracker.home_command()
            else:
                actions = string_to_action_command(kinematics_input)
                command_str = self.motor_state_tracker.action_to_motor_command(actions)
            self.send_command(command_str)

    def raw_mode(self):
        while True:
            print('WARNING: raw_mode does not track motor state, homing disabled')
            raw_command = input("Input command (or '=' to exit): ")
            if raw_command == '=':
                break
            self.send_command(raw_command)


    def run(self):
        """Main loop to select and run modes."""
        while True:
            picker = input("Mode selection:(s)Scanner (auto), (n) Notation, (r) Raw motor, (i) Inverse kinematics: ")
            mode_function = self.modes.get(picker)
            if mode_function:
                mode_function()
            else:
                print("Invalid selection. Try again.")

# Run the controller
if __name__ == "__main__":
    controller = RobotController()
    controller.run()