import time

import serial


class MotionController:
    def __init__(self, port= '/dev/tty.usbmodem20793672524E1', feedrate=10000):
        self.default_feedrate = feedrate

        self.connection = serial.Serial(port, 115200)
        self.init_controller_settings()

    def init_controller_settings(self):
        # microstepping
        # ser.write(b'M350 X16 Y16 Z16 E16 I1\r\n')
        # steps per mm
        self.run_gcode('M92 X80 Y80 Z80 E100', silent=True)
        # set max acceleration
        # remember, z is actually x, y is y, x is actually z
        self.run_gcode(f'M201 X3000 Y2000 Z4000 E5000', silent=True)
        # acceleration
        self.run_gcode(f'M204 P30000 T30000', silent=True)
        # max feedrate
        self.run_gcode('M203 X200 Y300 Z500 E5000', silent=True)
        # motor current
        self.run_gcode('M906 X1800 Z1500 Y1800', silent=True)
        # reverse Y
        # self.run_gcode('M907 X1

    def run_gcode(self, gcode: str, silent: bool = False):
        if not gcode.endswith('\r\n'):
            gcode += '\r\n'
        gcode_encoded = gcode.encode()
        self.__run_and_wait_for_completion(gcode_encoded, silent)

    def __run_and_wait_for_completion(self, gcode: bytes, silent: bool):
        self.connection.write(gcode)
        # wait 200ms
        # time.sleep(0.1)
        if not silent:
            print(self.connection.readline().decode().strip())
        self.connection.write(b"M400\r\n")
        # time.sleep(0.1)
        while True:
            response = self.connection.readline().decode().strip()
            if not silent:
                print('\t'.join([gcode.decode(), response]))
            if response == "ok":
                break
            # time.sleep(0.1)

    def home(self, home_x=True, home_y=True, home_z=False):
        print("Homing....")
        # set homing speed and sensitivity
        # touch off all axis limit switches
        cmd = 'G28'
        if home_x:
            cmd += ' Z0'
        if home_y:
            cmd += ' Y0'
        if home_z:
            cmd += ' X0'
        if not any([home_x, home_y, home_z]):
            print("No axis to home")
            return

        self.run_gcode(cmd)

    def disable_steppers(self):
        self.run_gcode("M84")

    def jog(self, *, x=None, y=None, z=None, feedrate=None):
        if x is None and y is None and z is None:
            print("No axis to jog")
            return
        # Z is driving X because the controller board has dual z outputs and i have dual x motors.
        # Y is Y. z is driven by x.
        self.run_gcode(f"G1 X{z} Y{y} Z{x}  F{feedrate or self.default_feedrate}")

    def pickup(self, z_height, feedrate=None):
        self.jog(z=z_height, feedrate=feedrate or self.default_feedrate)
        self.jog(z=10)

    def set_feedrate(self, feedrate):
        self.default_feedrate = feedrate


if __name__ == "__main__":
    ctrl = MotionController(feedrate=40000)
    ctrl.home(home_x=True, home_y=True, home_z=True)
    ctrl.jog(x=200)
    ctrl.jog(y=150, x=300)
    ctrl.pickup(60)
    ctrl.jog(y=200, x=100)
    ctrl.pickup(60)
    ctrl.jog(x=300)
    ctrl.pickup(60)
    ctrl.jog(x=5, y=5)
    ctrl.pickup(60)


    # for _ in range(1):
    #     ctrl.jog(10, 0, 0)
        # ctrl.jog(40, 40, 40, feedrate=feedrate)

    ctrl.disable_steppers()
