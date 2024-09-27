# Description: This script is used to control the CNC machine using the GRBL firmware.
# 9/26/2024

# CNC Gcode Reference:
# https://www.sainsmart.com/blogs/news/grbl-v1-1-quick-reference?srsltid=AfmBOor0BcEKPj1iHUnPeY6PzX4zSkUKPYC3nDTWs908b8GcVDu0xvKr

import serial           # serial for comms with CNC; pip install pyserial
# https://pyserial.readthedocs.io/en/latest/pyserial_api.html

import time             # for delay


class Cnc:

    port_name = 'COM?'
    msg_welcome = ''
    debug_serial = False

    def __init__ (self, port_name):

        self.s = serial.Serial(port = port_name, baudrate = 115200, timeout = 5)   # establish serial connection with COM8 @ 115200 baud rate
        err_empty = self.serial_read_response_line()
        self.msg_welcome = self.serial_read_response_line()
        
    def close (self):
        self.s.flush()
        self.s.close()

    def serial_send_command (self, cmd):
        str = cmd + "\r"
        self.s.write(str.encode())
        if self.debug_serial:
            print("Serial >> " + str)

    def serial_read_response_line (self):
        ch = self.s.read_until(b"\r\n")
        if self.debug_serial:
            print("Serial << ", ch)
        return ch

    def move_xyz_to (self, direction, pos):
        self.serial_send_command(f"G0 {direction}{pos}")
        ch = self.serial_read_response_line()
        if ch != b"ok\r\n":
            print("Error: expected 'ok' but received something else")
        else:
            while cnc.get_current_mode() != "Idle":
                # print(cnc.get_current_position())
                time.sleep(0.1)

    
    def get_status (self):
        self.serial_send_command("?")
        data = self.serial_read_response_line()
        ch = self.serial_read_response_line()
        if ch != b"ok\r\n":
            print("Error: expected 'ok' but received something else")
        else:
            return data
        
    def get_current_mode (self):
        data = self.get_status()
        str = data.decode().strip().split("|")[0]
        str = str[1:]              # remove the "<" at the beginning
        return str

    def get_current_position (self):
        data = self.get_status()
        str = data.decode().strip().split("|")[1]
        str = str[5:]
        val = str.split(",")
        return [float(val[0]) , float(val[1]) , float(val[2])]

port_name = 'COM3'

cnc = Cnc(port_name)


cnc.move_xyz_to("X",20)
cnc.move_xyz_to("X",0)
cnc.move_xyz_to("Y",20)
cnc.move_xyz_to("Y",0)
cnc.move_xyz_to("Z",2)
cnc.move_xyz_to("Z",0)
cnc.get_status()

cnc.close()

print(cnc.msg_welcome)
