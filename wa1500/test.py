import serial
import time

class Wavemeter:
    def __init__(self,address,baudrate=1200,timeout=2):
        self.timeout=timeout
        self.device = serial.Serial(address,baudrate=baudrate,timeout=self.timeout)
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
        if not self.device.isOpen(): return "WA-1500 link closed"



# Testing
wavemeter = Wavemeter("COM5")

print wavemeter.read_frequency()


for i in range(20):
    # time.sleep(0.1)
    print wavemeter.read_frequency()
print wavemeter.close()
