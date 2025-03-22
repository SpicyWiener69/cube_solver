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
from notation_movement_v2 import notation_to_clean_dataclasses,string_to_action_command,MotorStateTracker

class RobotController:
    def __init__(self, port_name='/dev/ttyACM0', baudrate=57600, timeout=3):
        """Initialize the serial connection and mode selection."""
        self.motor_state_tracker = MotorStateTracker()
        self.port = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
        self.modes = {
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

    def notation_mode(self):
        while True:
            raw_notation = input("Input notation (or '=' to exit): ")
            if raw_notation == '=':
                break
            dataclasses = notation_to_clean_dataclasses(raw_notation.split())
            command_str = self.motor_state_tracker.dataclass_to_motor_command(dataclasses)
            self.send_command(command_str)

    def raw_mode(self):
        while True:
            raw_command = input("Input command (or '=' to exit): ")
            if raw_command == '=':
                break
            elif raw_command == 'home':
                raw_command = self.motor_state_tracker.home_command()
            self.send_command(raw_command)

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

    def run(self):
        """Main loop to select and run modes."""
        while True:
            picker = input("Mode selection: (n) Notation, (r) Raw motor, (i) Inverse kinematics: ")
            mode_function = self.modes.get(picker)
            if mode_function:
                mode_function()
            else:
                print("Invalid selection. Try again.")

# Run the controller
if __name__ == "__main__":
    controller = RobotController()
    controller.run()