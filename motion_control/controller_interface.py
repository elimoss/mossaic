import time


class ImagerMotionController:
    def __init__(self, port, feedrate=3000):
        from printrun import printcore

        def _monkeypatch_printcore_horseshit(printcore):
            if printcore.send_thread:
                printcore.stop_send_thread = True
                try:
                    printcore.send_thread.join()
                except RuntimeError:
                    # print("Caught the join in a horrible monkeypatch, continuing")
                    pass
                printcore.send_thread = None

        printcore.printcore._stop_sender = _monkeypatch_printcore_horseshit

        p = printcore.printcore(port, 115200)  # or p.printcore('COM3',115200) on Windows
        p.loud = True
        print("Initializing.....")
        time.sleep(1)  # allow to connect 🙄
        if not p.online:
            raise Exception(f"Could not connect to robot on {port}")
        self.feed = feedrate
        self.printcore = p

        self.printcore.send_now('G21')  # set units to mm
        self.printcore.send_now('M203 X600000 Z600000 Y50000')  # set max feedrate super high (still limited by firmware)

    def close(self):
        self.printcore.cancelprint()
        self.printcore.disconnect()
    def home(self):
        # touch off all axis limit switches
        self._move(['G28'])
        # park position
        self.park()

    def park(self):
        self._move(['G0 Z100 F2000', 'G0 X10 Y300 F3000'])  # up and back

    def move_z(self, z_height, cam=None, speed_factor=0.8):
        # print(f"Moving to {z_height}")
        images = self._move([f'G1 Z{z_height} F{self.feed*speed_factor}'], cam)
        return images

    def vertical_image_sweep(self, start, stop, cam):
        self.move_z(start, speed_factor=0.7)
        images = self.move_z(stop, cam, speed_factor=0.6)
        # print(f"captured {len(images)} images")
        return images

    def _move(self, gcode: list):
        from printrun import gcoder
        gcode += ['G4 P100']
        gcode = gcoder.LightGCode(gcode)

        # this has been throwing RuntimeError: cannot join thread before it is started
        # workaround by trying it a few times
        self.printcore.startprint(gcode)  # this will start a print
        images = []
        # print(f"Well {well}: ({x}, {y})")

        return images

    def jog(self, x, y, force_feed=None):
        self._move([f"G0 X{x} Y{y} F{force_feed or self.feed}"])
        while controller.printcore.printing:
            time.sleep(0.1)


if __name__ == "__main__":
    controller = ImagerMotionController("/dev/tty.usbmodem20793672524E1", 6000)
    dest1 = 0
    dest2 = 100
    curr_dest = dest1
    for feedrate in range(5000, 50000, 1000):
        print(feedrate)
        controller.jog(curr_dest, curr_dest, force_feed=feedrate)
        curr_dest = dest2 if curr_dest == dest1 else dest1

    controller.close()

