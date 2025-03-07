import serial
from notation_movement_v2 import convert_all

mode = 'MANUAL'

port = serial.Serial(port = '/dev/ttyACM0', baudrate = 57600)

if mode == 'MANUAL':
    while True:
        raw_notation = input("input command:")
        if raw_notation == '=':   #session end
            break
        raw_notation = raw_notation.split(' ')
        
        command_str = convert_all(raw_notation)
        command_str+='#' #command end 
        port.write(command_str.encode('ascii'))