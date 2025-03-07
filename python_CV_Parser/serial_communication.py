import serial
from notation_movement_v2 import convert_all

mode = 'Manual'

port = serial.Serial(port = '/dev/ttyACM0', baudrate = 57600,timeout=3)

if mode == 'Notation':
    while True:
        raw_notation = input("input notation:")
        if raw_notation == '=':   #session end
            break
        raw_notation = raw_notation.split(' ')
        
        command_str = convert_all(raw_notation)
        command_str+='#' #command end 
        print(command_str)
        port.write(command_str.encode('ascii'))
        print(port.read_until(expected=b'#'))

elif mode == 'Manual':
    while True:
        raw_command = input("input command:") 
        if raw_command == '=':
            break
        port.write(raw_command.encode('ascii'))
        print(port.read_until(expected=b'#'))
