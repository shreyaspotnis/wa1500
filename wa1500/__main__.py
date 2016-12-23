"""Reads and publishes the wa1500 wavemeter an a zeromq socket."""

import time
import serial
import random
import zmq
import datetime
import sys
import argparse

parser = argparse.ArgumentParser(description='Reads and publishes the wa1500'
                                 'wavemeter an a zeromq socket.\n'
                                 'Example usage: wa1500.py --serialport COM5'
                                 ' --publishport 557 --topic wa1500')
parser.add_argument("-s", "--serialport", type=str,
                    help='Serial port to use to communicate with the'
                         'wavemeter. e.g /dev/ttyUSB0 for linux, '
                         'COM5 for windows',
                    default='COM5')
parser.add_argument("-p", "--publishport", type=int,
                    help='zeromq port to use to broadcast the wavemeter'
                         'reading.',
                    default=5557)
parser.add_argument("-t", "--topic", type=str,
                    help='topic to use when broadcasting. e.g wa1500-lab1',
                    default='wa1500')

args = parser.parse_args()


publish_port = args.publishport
topic = args.topic
serial_device_path = args.serialport

zmq_context = zmq.Context()
pub_socket = zmq_context.socket(zmq.PUB)
pub_socket.bind("tcp://*:%s" % publish_port)


class WA1500:

    def __init__(self, address, baudrate=1200, timeout=2):

        self.timeout = timeout
        self.device = serial.Serial(address, baudrate=baudrate,
                                    timeout=self.timeout)
        self.device.flush()

    def read_frequency(self):
        self.device.write("@Q\r\n")
        self.device.flushInput()
        err_msg = 'ok'
        try:
            s = self.device.readline()
            print('recvd: %s' % s)
            self.device.flushOutput()
            if 'LO SIG' in s:
                err_msg = 'low signal'
                print(err_msg)
                frequency = -1.0
            elif 'HI SIG' in s:
                err_msg = 'high signal'
                print(err_msg)
                frequency = -1.0
            elif '~' in s:
                err_msg = 'possibly multimode'
                print(err_msg)
                frequency = float(s.split(',')[0][1:])
            else:
                frequency = float(s.split(',')[0])
        except KeyboardInterrupt:
            raise
        except:
            # write better error handling here
            frequency = -1.0
            err_msg = 'unknown error'
        return frequency, err_msg

    def close(self):
        self.device.close()
        if not self.device.isOpen():
            return "WA-1500 link closed"
        else:
            return "WA-1500 close error"


class WA1500_dummy:

    def __init__(self, address, baudrate=1200, timeout=2):
        pass

    def read_frequency(self):
        return 375000.00 + random.gauss(0., 0.1)

    def close(self):
        pass

done = False
wavemeter_define = False
while not done:
    try:
        wavemeter = WA1500(serial_device_path)
        wavemeter_define = True
        while True:
            freq, err_msg = wavemeter.read_frequency()
            dt = str(datetime.datetime.now())
            send_string = "%s %s %f %s" % (topic, dt, freq, err_msg)
            print(send_string)
            pub_socket.send(send_string)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print wavemeter.close()
        pub_socket.close()
        done = True
    except serial.serialutil.SerialException as e:
        print "Serial Exception: ", e
        if wavemeter_define:
            wavemeter.close()
            wavemeter_define = False
        time.sleep(1.0)
