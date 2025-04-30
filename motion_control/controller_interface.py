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
        # self.run_gcode(f'M201 X1400 Y2000 Z2000 E5000', silent=True)  # x stage acceleration is high due to a resonance issue
        self.run_gcode(f'M201 X800 Y1000 Z2000 E5000', silent=True)  # x stage acceleration is high due to a resonance issue
        # acceleration
        self.run_gcode(f'M204 P30000 T30000', silent=True)
        # max feedrate
        # self.run_gcode('M203 X450 Y500 Z300', silent=True)
        self.run_gcode('M203 X900 Y400 Z300', silent=True)
        # motor current
        self.run_gcode('M906 X300 Y1200 Z2200', silent=True)  # this still works on the old pin assignments, so reducing the z current means x should be reduced
        # set microstepping
        # self.run_gcode('M350 X16 Y16 Z16', silent=True)

        # fan on
        self.run_gcode('M106')

    def run_gcode(self, gcode: str, silent: bool = False, wait: bool = True):
        # maybe fill in feedrate
        if gcode.startswith('G1'):
            if 'F' not in gcode:
                gcode += f" F{self.default_feedrate}"
        if not gcode.endswith('\r\n'):
            gcode += '\r\n'
        gcode_encoded = gcode.encode()
        self.__run(gcode_encoded, silent, wait)

    def __run(self, gcode: bytes, silent: bool, wait: bool):
        self.connection.write(gcode)
        # wait 200ms
        # time.sleep(0.1)
        # read until ok

        responses = []
        while True:
            response = self.connection.readline().decode().strip()
            if response == "ok":
                break
            if response.startswith("Error:"):
                print(response)
                break
            if response.startswith("echo:"):
                continue
            responses.append(response)
        if not silent:
            print('\t'.join([gcode.decode(), '\t'.join(responses)]))
        # time.sleep(0.1)
        if wait:
            self.connection.write(b"M400\r\n")
            while True:
                response = self.connection.readline().decode().strip()
                if not silent:
                    print('\t'.join([gcode.decode(), response]))
                if response == "ok":
                    break
                # time.sleep(0.1)

    def home(self, home_x=False, home_y=False, home_z=False):
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
        self.run_gcode("M84", silent=True)

    def jog(self, *, x=None, y=None, z=None, feedrate=None):
        if x is None and y is None and z is None:
            print("No axis to jog")
            return
        if x is not None:
            cmd = f"G1 X{x}"
            self.run_gcode(cmd + f" F{feedrate or self.default_feedrate}")
        if y is not None:
            cmd = f"G1 Y{y}"
            self.run_gcode(cmd + f" F{feedrate or self.default_feedrate}")
        if z is not None:
            cmd = f"G1 Z{z}"
            self.run_gcode(cmd + f" F{feedrate or self.default_feedrate}")

    def pickup(self, z_height, feedrate=None):
        self.jog(z=-10, feedrate=feedrate or self.default_feedrate)
        self.jog(z=z_height)

    def set_feedrate(self, feedrate):
        self.default_feedrate = feedrate

    def pen_down_setup(self):
        self.home(home_z=True)
        self.jog(z=13.5)

    def run_file_from_sd_card(self, gcode_filepath: str, feed_multiplier: int = 100):
        # run file from sd card
        self.run_gcode(f'M23 {gcode_filepath}', wait=False, silent=False)
        self.run_gcode(f'M220 S{feed_multiplier}')
        self.run_gcode('M24', wait=True, silent=False)
        # wait for completion

    def pen_up(self):
        self.jog(z=60)


if __name__ == "__main__":
    ctrl = MotionController(feedrate=3000)

    # ctrl.home(home_x=True, home_y=True, home_z=True)
    ctrl.home(home_z=True)
    ctrl.pen_down_setup()
    input()
    ctrl.pen_up()
    input()
    ctrl.run_file_from_sd_card('bigmako', feed_multiplier=400)


    # list files
    # ctrl.run_gcode('M20', wait=False, silent=False)

    # ctrl.disable_steppers()
