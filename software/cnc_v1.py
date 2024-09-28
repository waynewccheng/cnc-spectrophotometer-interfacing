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
    s = None                           # serial port object

    def __init__ (self, port_name):
        self.port_name = port_name
        self.serial_open(port_name)

    def __del__ (self):
        self.serial_close()
       
    #
    # Serial port related methods
    #     

    def serial_open (self, port_name):
        try:
            self.s = serial.Serial(port = port_name, baudrate = 115200, timeout = 5)   # establish serial connection with COM8 @ 115200 baud rate
            # the CNC is expected to respond to any command within 5 seconds

            # wait for the CNC to initialize
            time.sleep(2)   
            
    #        self.serial_send_command("$X")
    #        self.serial_read_response_line()
            
            # get the welcome message
            err_empty = self.serial_read_response_line()
            self.msg_welcome = self.serial_read_response_line()

        except:
            print("Error: unable to open serial port")
            self.s = None

    def serial_close (self):
        self.s.flush()
        self.s.close()

    def serial_send_command (self, cmd):
        str = cmd + "\r"
        self.s.write(str.encode())
        
        if self.debug_serial:
            print("Serial >> " + str)

        # add some delay for all commands
        time.sleep(0.1)

    def serial_read_response_line (self):
        if self.debug_serial:
            print(f"  bytes in buffer to be read -- {self.s.in_waiting}")
        
        ch = self.s.read_until(b"\r\n")     # wait for the expected data to arrive 

        if self.debug_serial:
            print("Serial << ", ch)
        return ch

    # 
    # CNC related methods
    #
    def move_x_y_z_to (self, direction, pos):
        self.serial_send_command(f"G0 {direction}{pos}")
        ch = self.serial_read_response_line()
        if ch != b"ok\r\n":
            print("Error: expected 'ok' but received something else - ")    
            print(ch)
        else:
            while self.get_current_mode() != "Idle":
                # print(cnc.get_current_position())
                time.sleep(0.1)

    def move_xyz_to (self, pos):
        self.serial_send_command(f"G0 X{pos[0]} Y{pos[1]} Z{pos[2]}")
        ch = self.serial_read_response_line()
        if ch != b"ok\r\n":
            print("Error: expected 'ok' but received something else - ")    
            print(ch)
        else:
            while self.get_current_mode() != "Idle":
                # print(cnc.get_current_position())
                time.sleep(0.1)

    def get_status (self):
        self.serial_send_command("?")
        data = self.serial_read_response_line()
        ch = self.serial_read_response_line()
        if ch != b"ok\r\n":
            print("Error: expected 'ok' but received something else")
            print(ch)
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


#
# Test code
#

# cnc = Cnc(port_name)

# cnc.move_x_y_z_to("X",20)
# cnc.move_x_y_z_to("X",0)
# cnc.move_x_y_z_to("Y",20)
# cnc.move_x_y_z_to("Y",0)
# cnc.move_x_y_z_to("Z",2)
# cnc.move_x_y_z_to("Z",0)
# cnc.get_status()

# cnc.serial_close()

# print(cnc.msg_welcome)
