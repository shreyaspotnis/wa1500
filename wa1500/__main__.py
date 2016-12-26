"""Reads and publishes the wa1500 wavemeter reading an a zeromq socket."""

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
                                 ' --publishport 5557 --topic wa1500')
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
parser.add_argument("--dummy", action='store_true',
                    help='Do not read wavemeter, publish random'
                         ' numbers instead.')

args = parser.parse_args()


class zmq_pub_dict:
    """Publishes a python dictionary on a port with a given topic."""

    def __init__(self, port, topic):
        zmq_context = zmq.Context()
        self.topic = topic
        self.pub_socket = zmq_context.socket(zmq.PUB)

        self.pub_socket.bind("tcp://*:%s" % port)
        print('Broadcasting on port {0} with topic {1}'.format(port,
                                                               topic))

    def send(self, data_dict):
        timestamp = time.time()
        send_string = "%s %f %s" % (self.topic, timestamp, repr(data_dict))
        print(send_string)
        self.pub_socket.send(send_string)

    def close(self):
        self.pub_socket.close()


publisher = zmq_pub_dict(args.publishport, args.topic)


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
        return 375000.00 + random.gauss(0., 0.1), 'ok'

    def close(self):
        pass

done = False
wavemeter_defined = False
while not done:
    try:
        if args.dummy:
            wavemeter = WA1500_dummy(args.serialport)
        else:
            wavemeter = WA1500(args.serialport)
        wavemeter_defined = True
        while True:
            freq, err_msg = wavemeter.read_frequency()
            data_dict = {'freq': freq,
                         'err_msg': err_msg}
            publisher.send(data_dict)

            time.sleep(0.5)
    except KeyboardInterrupt as e:
        print "KeyboardInterrupt: exiting"
        print wavemeter.close()
        done = True
    except serial.serialutil.SerialException as e:
        print "SerialException: ", e
        if wavemeter_defined:
            wavemeter.close()
            wavemeter_defined = False
        time.sleep(1.0)

publisher.close()
