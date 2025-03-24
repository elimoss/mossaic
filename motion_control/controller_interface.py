import time

import serial


class MotionController:
    def __init__(self, port= '/dev/tty.usbmodem20793672524E1', feedrate=10000):
        self.default_feedrate = feedrate

        self.connection = serial.Serial(port, 115200)



        # microstepping
        # ser.write(b'M350 X16 Y16 Z16 E16 I1\r\n')
        # steps per mm
        self.run_gcode('M92 X80 Y80 Z80 E100')
        # set max acceleration
        self.run_gcode(f"M201 X1 Y6000 Z3000 E5000")
        # acceleration
        self.run_gcode(f"M204 P10000 T10000")
        # self.connection.readline()
        # junction deviation
        # self.run_gcode('M205 J0.05')
        # max feedrate
        self.run_gcode('M203 X1 Y30000 Z40000 E5000')
        # motor current
        self.run_gcode("M906 X1500 Z1800 Y1500")

    def run_gcode(self, gcode: str):
        if not gcode.endswith('\r\n'):
            gcode += '\r\n'
        gcode_encoded = gcode.encode()
        self.__run_and_wait_for_completion(gcode_encoded)

    def __run_and_wait_for_completion(self, gcode: bytes):
        self.connection.write(gcode)
        # wait 200ms
        time.sleep(0.1)
        print(self.connection.readline().decode().strip())
        self.connection.write(b"M400\r\n")
        time.sleep(0.1)
        while True:
            response = self.connection.readline().decode().strip()
            print('\t'.join([gcode.decode(), response]))
            if response == "ok":
                break

    def home(self, home_x=True, home_y=True, home_z=False):
        print("Homing....")
        # set homing speed and sensitivity
        # touch off all axis limit switches
        cmd = 'G28'
        if home_x:
            cmd += ' X0'
        if home_y:
            cmd += ' Y0'
        if home_z:
            cmd += ' Z0'
        if not any([home_x, home_y, home_z]):
            print("No axis to home")
            return

        self.run_gcode(cmd)

    def disable_steppers(self):
        self.run_gcode("M84")

    def jog(self, x, y, feedrate=None):
        # Z is driving X because the controller board has dual z outputs and i have dual x motors.
        # Y is Y. there is no Z or E.
        self.run_gcode(f"G1 Z{x} Y{y} F{feedrate or self.default_feedrate}")


if __name__ == "__main__":
    ctrl = MotionController()
    x_feedrate = 40000
    y_feedrate = 60000
    ctrl.jog(200, 0,  feedrate=x_feedrate)
    ctrl.jog(200, 200, feedrate=y_feedrate)
    ctrl.jog(0, 200, feedrate=x_feedrate)
    ctrl.jog(0, 0, feedrate=y_feedrate)
    ctrl.disable_steppers()
