import serial
from notation_movement_v2 import notation_to_motor_commands,usr_abs_to_motor_commands

mode = ''

port = serial.Serial(port = '/dev/ttyACM0', baudrate = 57600,timeout=3)

while True:
    picker = input("mode selection(n for Notation control, r for Raw motor control, i for Inverse kinematics):")
    if picker == 'n':
        mode = 'Notation'
    elif picker == 'r':
        mode = 'raw'
    elif picker == 'i':
        mode = 'inverse'

    if mode == 'Notation':
        while True:
            raw_notation = input("input notation:")
            if raw_notation == '=':   #session end
                break
            raw_notation = raw_notation.split(' ')
            
            command_str = notation_to_motor_commands(raw_notation)
            command_str+='#' #command end 
            print(command_str)
            port.write(command_str.encode('ascii'))
            print(port.read_until(expected=b'#'))

    elif mode == 'raw':
        while True:
            raw_command = input("input command:") 
            if raw_command == '=':
                break
            port.write(raw_command.encode('ascii'))
            print(port.read_until(expected=b'#'))
    
    elif mode == 'inverse':
        while True:
            str = input("input kinematics:") 
            if str == '=':
                break
            command_str = usr_abs_to_motor_commands(str)
            command_str+='#' #command end 
            port.write(command_str.encode('ascii'))
            print(port.read_until(expected=b'#'))