import serial
import time

from motor_state_tracker import MotorStateTracker, string_to_action_command
from detect import Detector
from notation_parser import NotationConvertor
from api_call import fetch_solution 
from logger import Logger

class  RobotController:
    def __init__(self, port_name='/dev/ttyACM0', baudrate=57600, timeout=400):
        """Initialize the serial connection and mode selection."""
        self.cubesize = None
        self.logger = Logger()
        self.port = serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout)
        self.modes = {
            's':self.scanner_mode,
            'n': self.notation_mode,
            'r': self.raw_mode,
            'i': self.inverse_kinematics_mode
        }

    def send_command(self, command:str):
        command += '#'  # Append command end character
        print(f'sending command of length {len(command)} char...')
        self.port.write(command.encode('ascii'))
        response = self.port.read_until(expected=b'}')
        print(f"task completed")
        
    def scanner_mode(self):
        try:
            cube_state = self._scan_six_sides()
            print(cube_state)
            solution = fetch_solution(cube_state=cube_state)
            if solution == ['is', 'already', 'solved']:
                print('already solved')
            else:
                print(f'solution found: {solution}')
                print("solve starting:")
                t0 = time.time()
                dataclasses = self.notation_convertor.to_dataclasses(solution)
                command = self.motor_state_tracker.dataclass_to_motor_command(dataclasses)
                self.send_command(command)
                t1 = time.time()
                execution_time = t1 - t0
                print(f'execution time in: {(execution_time):.2f}s')
                self.logger.add_data(success=1, solve_time=execution_time)
                self.logger.save()
        except KeyboardInterrupt:
            print("KeyboardInterrupt detected! Logging error...")
            self.logger.add_data(success=0)
            self.logger.save()

    def _scan_six_sides(self) -> str:
        moveset = [['y'],['y'],['y'],["y", "x'"],["x2"]]
        print("starting stream...")
        detector = Detector(cubesize=self.cubesize, debug = False)
        t0 = time.time()
        #align cube before detection
        command = self.motor_state_tracker.cube_alignment_command()
        self.send_command(command)
        time.sleep(2)

        detector.start()
        detector.display_bboxes()
        detector.detect_face()
        for move in moveset:
            dataclasses = self.notation_convertor.to_dataclasses(move)
            command = self.motor_state_tracker.dataclass_to_motor_command(dataclasses)
            self.send_command(command)
            time.sleep(1.5)
            detector.display_bboxes()
            detector.detect_face()

        # align back to original orientation
        command = self.motor_state_tracker.dataclass_to_motor_command(self.notation_convertor.to_dataclasses(["x'"]))
        self.send_command(command)

        t1 = time.time()    
        detection_time = t1 - t0
        self.logger.add_data(detection_time=detection_time, cubesize=self.cubesize)
        print(f"ending video stream. Detection took: {t1 - t0}s")
        cubestate = detector.solve_color()
        return cubestate

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
                dataclasses = self.notation_convertor.to_dataclasses(input_str.split())
                command = self.motor_state_tracker.dataclass_to_motor_command(dataclasses)
                self.send_command(command)
        # reset after a session
        command = self.motor_state_tracker.home_command()
        self.send_command(command)

    def inverse_kinematics_mode(self):
        while True:
            input_str = input("Input kinematics (or '=' to exit): ")
            if input_str == '=':
                break
            elif input_str == 'home':
                command_str = self.motor_state_tracker.home_command()
            else:
                actions = string_to_action_command(input_str)
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
            input_str = input("Input cube_layer (or '=' to exit): ")
            if input_str == '=':
                break
            if int(input_str) not in range(2,5):
                print("Invalid selection. Try again.")
            else:
                self.cubesize = int(input_str)
                self.motor_state_tracker = MotorStateTracker(cubesize=self.cubesize)
                self.notation_convertor = NotationConvertor(cubesize=self.cubesize)
                while True:
                    picker = input("Mode selection:(s)Scanner, (n) Notation, (r) Raw motor, (i) Inverse kinematics. type '=' to exit:")
                    if picker == '=':
                        break
                    mode_function = self.modes.get(picker)
                    if mode_function:
                        mode_function()
                    else:
                        print("Invalid selection. Try again.")

 # Run the controller
if  __name__ ==  "__main__":
    controller = RobotController()
    controller.run()