import time
import serial
import random
import zmq

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
        s = self.device.readline()
        self.device.flushOutput()
        frequency = float(s.split(',')[0])
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

wavemeter = WA1500_dummy('COM5')

try:
    for i in range(20):
        topic = 1
        freq = wavemeter.read_frequency()
        print "%d %f" % (topic, freq)
        pub_socket.send("%d %f" % (topic, freq))
        time.sleep(0.1)
except KeyboardInterrupt:
    print wavemeter.close()
    pub_socket.close()
else:
    print wavemeter.close()
    pub_socket.close()

