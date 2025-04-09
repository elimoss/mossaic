import time

import serial


class MotionController:
    def __init__(self, port= '/dev/tty.usbmodem20793672524E1', feedrate=10000):
        self.default_feedrate = feedrate

        self.connection = serial.Serial(port, 115200)
        self.init_controller_settings()

    def init_controller_settings(self):
        # remember, z is actually x, y is y, x is actually z

        # steps per mm
        self.run_gcode('M92 X80 Y80 Z80', silent=True)
        # set max acceleration
        self.run_gcode(f'M201 X1000 Y800 Z4000 E5000', silent=True)  # x stage acceleration is high due to a resonance issue
        # acceleration
        self.run_gcode(f'M204 P30000 T30000', silent=True)
        # max feedrate
        self.run_gcode('M203 X200 Y500 Z700', silent=True)
        # motor current
        self.run_gcode('M906 X1800 Z1800 Y1800', silent=True)
        # override z limit
        self.run_gcode('M211 S0', silent=True)
        # set microstepping
        # self.run_gcode('M350 X16 Y16 Z16', silent=True)


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
        cmd = "G1"
        if x is not None:
            cmd += f" Z{x}"
        if y is not None:
            cmd += f" Y{y}"
        if z is not None:
            cmd += f" X{z}"
        self.run_gcode(cmd + f" F{feedrate or self.default_feedrate}")

    def pickup(self, z_height, feedrate=None):
        self.jog(z=z_height, feedrate=feedrate or self.default_feedrate)
        self.jog(z=10)

    def set_feedrate(self, feedrate):
        self.default_feedrate = feedrate


if __name__ == "__main__":
    ctrl = MotionController(feedrate=40000)
    # ctrl.home(home_x=True, home_y=True, home_z=True)

    ctrl.jog(x=100, feedrate=30000)
    ctrl.jog(x=10, feedrate=30000)
    ctrl.jog(x=500, y=250)
    ctrl.jog(x=300)
    ctrl.pickup(60)
    ctrl.jog(y=150, x=300)
    ctrl.pickup(60)
    ctrl.jog(y=200, x=100)
    ctrl.pickup(60)
    ctrl.jog(x=300)
    ctrl.pickup(60)
    ctrl.jog(x=5, y=5)
    ctrl.pickup(60)

    for _ in range(1):
        # ctrl.set_feedrate(15000)
        ctrl.jog(x=500, y=250)
        ctrl.jog(x=300)

    ctrl.jog(x=50, y=50)

    ctrl.disable_steppers()
