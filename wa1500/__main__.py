import time
import serial
import random
import zmq
import datetime

publish_port = "5556"

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
        try:
            s = self.device.readline()
            print('recvd: %s' % s)
            self.device.flushOutput()
            frequency = float(s.split(',')[0])
        except KeyboardInterrupt:
            raise
        except:
            # write better error handling here
            frequency = -1.0
        return frequency

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

wavemeter = WA1500('COM5')

try:
    while True:
        topic = 'wa1500'  # This will be useful when there are multiple streams
                          # to watch
        freq = wavemeter.read_frequency()
        dt = str(datetime.datetime.now())
        print "%s %s %f" % (topic, dt, freq)
        pub_socket.send("%s %s %f" % (topic, dt,freq))
        time.sleep(0.1)
except KeyboardInterrupt:
    print wavemeter.close()
    pub_socket.close()
else:
    print wavemeter.close()
    pub_socket.close()

