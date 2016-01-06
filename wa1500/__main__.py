import time
import serial

# init RS232 port COM1, 2400 baud, 8 data bits, no
# parity, 1 stop bit

# wa1500 = serial.Serial(port='COM3', baudrate=1200,
#                        parity=serial.PARITY_NONE,
#                        stopbits=serial.STOPBITS_TWO,
#                        bytesize=serial.EIGHTBITS)

wa1500 = serial.Serial(port='COM5', baudrate=9600,
                       parity=serial.PARITY_NONE,
                       stopbits=serial.STOPBITS_TWO,
                       bytesize=serial.EIGHTBITS)


print 'Is port open?', wa1500.isOpen()

input = '@Q'
wa1500.write(input + '\r\n')
out = ''
# let's wait one second before reading output
# (let's give device time to answer)
time.sleep(1)
while wa1500.inWaiting() > 0:
    out += wa1500.read(1)

if out != '':
    print ">>" + out

wa1500.close()
