import time
import serial
import random
import zmq
import datetime
import sys


publish_port = "5559"

if len(sys.argv) >= 2:
    serial_device_path = sys.argv[1]
else:
    serial_device_path = '/dev/ttyUSB0'

if len(sys.argv) == 3:
    topic = sys.argv[2]
else:
    topic = 'wa1500'  # This will be useful when there are multiple streams
                      # to watch

zmq_context = zmq.Context()
pub_socket = zmq_context.socket(zmq.PUB)
pub_socket.bind("tcp://*:%s" % publish_port)


class WA1500:

    def __init__(self, address, baudrate=1200, timeout=2):

        self.timeout = timeout
        self.device = serial.Serial(address, baudrate=baudrate,
        timeout=self.timeout)
        self.device.flush()
    
    def voltageToWavelength (self):
        #The formula gets the user to input the analog voltage read from the wavemeter
        #And outputs the wavelength being read
        #This function ignores the offset
        try: 
            AnalVoltage = float(input("Enter the Analog Voltage: "))
            Deviation = (AnalVoltage * float(analogres) / 0.0049)
            Wavelength = float(setpoint) + Deviation
            print ("The wavelength is: " + str(Wavelength))
            print ("\n")
            
        except KeyboardInterrupt:
            raise
        except:
            print ('Of all places to mess up, here? Really?') #Seriously?
        return 
        
    def front_panel (self):
        #This function takes the query from the wavemeter and outputs
        #the LEDS that are lit on the wavemeter 
    
        self.device.write("@Q\r\n") #Reading Query from Wavemeter
        self.device.flushInput()
        s = self.device.readline()

        try:
            #Dictionaries provided by WA1500 manual
            LeftPanelDict = {2000 : "Averaging - OFF", 1000 : "Averaging - ON",  800 : "Resolution - AUTO",  \
            400 : "Resolution - FIXED", 200 : "Medium - Vacuum", 100 : "Medium - Air", \
            80 : "Display - Deviation", 40 : "Display - Wavelength", 24 : "UNITS - GHZ", 12 : "UNITS - cm^-1", 9 : "UNITS - nm"}
            LeftPanelList = [2000, 1000, 800, 400, 200, 100, 80, 40, 24, 12, 9]
            
            RightPanelDict = {400 : "Input Attenuator - Manual", 200 : "Input Attenuator - Auto", 100: "REMOTE", \
            80 : "SETUP Restore/Save", 40 : "Humidity", 20 : "Temperature", 10 : "Pressure", 8 : "Analog Resolution", \
            4 : "Number Averagered", 2 : "Setpoint", 1 : "Display Resolution"}
            RightPanelList = [400, 200, 100, 80, 40, 20, 10, 8, 4, 2, 1]    
 
            LED1 = float(s.split(',')[1][0:]) #Query value for left panel information 
            LED2 = float(s.split(',')[2][0:]) #Query value for right panel information

            print ("The following is on:\n")
            for number in LeftPanelList:
                if (number <= LED1):
                    print (LeftPanelDict[number])
                    LED1 -= number

            for number in RightPanelList:
                if (number <= LED2):
                    if (number == 2) :
                         self.device.write("@\x26\r\n") #Hard Command Setpoint to turn off
                    if (number == 8) :
                        self.device.write("@\x24\r\n") #Hard Command Analog to turn off    
                    print (RightPanelDict[number])
                    LED2 -= number
            if LED2 != 0:
                print ("something is wrong") #All buttons should have been processed by this point        
            if LED1 != 0:
                print ("something is wrong") #All buttons should have been processed by this point
            print ("\n")
        except KeyboardInterrupt:
            raise
        except:
            print ('Nothing is ok') #Well, something is wrong
        return 
    
    def inputNumbers (self, num):
        #This function takes a number and hardcodes it to the wavemeter in an inefficient manner because \x is not a nice string
        for i in range (len(num)):
            if num [i] == ".":
                self.device.write("@\x0B\r\n") #Hard Command Decimal 
            elif (num [i] == "0") :
                self.device.write ("@\x00\r\n") #Hard Command for number 0
            elif (num [i] == "1") :
                self.device.write ("@\x01\r\n") #Hard Command for number 1
            elif (num [i] == "2") :
                self.device.write ("@\x02\r\n") #Hard Command for number 2
            elif (num [i] == "3") :
                self.device.write ("@\x03\r\n") #Hard Command for number 3
            elif (num [i] == "4") :
                self.device.write ("@\x04\r\n") #Hard Command for number 4
            elif (num [i] == "5") :
                self.device.write ("@\x05\r\n") #Hard Command for number 5
            elif (num [i] == "6") :
                self.device.write ("@\x06\r\n") #Hard Command for number 6
            elif (num [i] == "7") :
                self.device.write ("@\x07\r\n") #Hard Command for number 7  
            elif (num [i] == "8") :
                self.device.write ("@\x08\r\n") #Hard Command for number 8  
            elif (num [i] == "9") :
                self.device.write ("@\x09\r\n") #Hard Command for number 9  
            else :
                print ("Some key you entered hurt my feelings")
            time.sleep (0.1) #Don't want to overclock front panel
        self.device.write ("@\x0C\r\n") #Hard Command for Enter
        return

    def setpoint(self):
        #This function allows the user to remotely set the setpoint and resolution of the wavemeter        
        self.device.write("@Q\r\n") #Reading Query from Wavemeter
        self.device.flushInput()
        s = self.device.readline()

        try:        
        
            #Sets units to nm
            while s.split(',')[1][-1] != "9" : #Checks the last digit of the query info for units
                self.device.write ("@\x27\r\n") #Hard Comand to Change Units
                self.device.write("@Q\r\n") #ReReading Query from Wavemeter
                self.device.flushInput()
                s = self.device.readline() #Updating s for new units
                time.sleep(0.1) #Don't want to overclock the front panel

            global setpoint, analogres 
            setpoint = str(input("Enter setpoint in nm: "))
            analogres = str(input("Enter Analog Resolution in nm: "))

            self.device.write("@\x26\r\n") #Hard Command Setpoint
            self.inputNumbers (setpoint) #Hardcodes user input Setpoint
            
            self.device.write("@\x24\r\n") #Hard Command Analong Res      
            self.inputNumbers (analogres) #Hardcodes user input analog res
            
            return "Setpoint and Analog Resolution have successfully been added"
        except KeyboardInterrupt:
            raise
        except:
            print ('Nuthing is ok') #Well, something is wrong 
        return 
    
    def close(self):
        self.device.close()
        if not self.device.isOpen():
            return "WA-1500 link closed"
        else:
            return "WA-1500 close error"

'''
class WA1500_dummy:

    def __init__(self, address, baudrate=1200, timeout=2):
        pass

    def read_frequency(self):
        return 375000.00 + random.gauss(0., 0.1)

    def close(self):
        pass
'''
done = False
wavemeter_define = False


while not done:
    try:
        wavemeter = WA1500(serial_device_path)
        wavemeter_define = True
        while True:
            wavemeter.front_panel()
            wavemeter.setpoint()
            wavemeter.voltageToWavelength()
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
