import traceback
import RPi.GPIO as GPIO
import time

class Wiegand:

    def __init__(self,pin_D0,pin_D1):
        self.even_parity=0
        self.odd_parity=0
        self.pin_D0=pin_D0
        self.pin_D1=pin_D1
        GPIO.setmode (GPIO.BOARD)
        GPIO.setup (self.pin_D0,GPIO.OUT)
        GPIO.setup (self.pin_D1,GPIO.OUT)
        GPIO.output(self.pin_D0,1)
        GPIO.output(self.pin_D1,1)

    def sendD0(self):
        GPIO.output(self.pin_D0,0)
        time.sleep(.0001)
        GPIO.output(self.pin_D0,1)
        time.sleep(.002)
        #print('0')

    def sendD1(self):
        GPIO.output(self.pin_D1,0)
        time.sleep(.0001)
        GPIO.output(self.pin_D1,1)
        time.sleep(.002)
        #print('1')

    def createParity(self,data, bits,useFacilityCode):
        _evenParity = 0
        _oddParity = 1
        tempData = 0
        b = 0

        if(not useFacilityCode):
            if(bits==34):
                data = data & 0x00FFFFFF    
        
            elif(bits==26):
                data = data & 0x00FFFF

    #34 bits -> use 32 to check parity ((34-2)/2) = 16 even / 16 odd
    #26 bits -> use 24 to check parity ((26-2)/2) = 12 even / 12 odd
        b = int((bits-2)/2)
        #print(bits)
        for i in range(0,b,1):
            tempData = data>>i
            if(tempData & 0x01):        #this count the qty of 1 and do a xor to complete the even parity;            
                _oddParity = _oddParity ^ 1           
                self.odd_parity=_oddParity
    
    
    #34 bits -> use 32 to check parity ((34-2)/2) = 16 even / 16 odd
    #26 bits -> use 24 to check parity ((26-2)/2) = 12 even / 12 odd
        tempData=0;
        for i in range(b,bits-2,1):   
            tempData = data>>i
            if(tempData & 0x01):        #this count the qty of 1 and do a xor to complete the odd parity;
                _evenParity = _evenParity ^ 1
                self.even_parity = _evenParity         


    def send(self,data, bits, useFacilityCode):
        try:
            tempData =0
            
            if(not useFacilityCode):
                if(bits==34):
                    data = data & 0x00FFFFFF #force facility (first 8 msb as 0) as 0x00
            
                elif(bits==26):
                    data = data & 0x00FFFF #force facility (first 8 msb as 0) as 0x00
            

            self.createParity(data,bits,useFacilityCode)
            tempData = data
            #send even parity 
            if(self.even_parity):
                self.sendD1()
            else:
                self.sendD0()
        
            if(bits==26):  #send 24 bits data wiegand
                for i in range(0,bits-2,1):

                    tempData = data << i
                    if(tempData & 0x00800000):
                        self.sendD1()
                    else:
                        self.sendD0()
                    
            elif(bits==34):      #send 32 bits data wiegand
                for i in range(0,bits-2,1):
                    tempData = data << i
                    if(tempData & 0x80000000):
                        self.sendD1()
                    else:
                        self.sendD0()
                    
        #send odd parity bit
            if(self.odd_parity):
                self.sendD1()
            else:
                self.sendD0()
        except Exception as e:
            print("ERRO_SEND_WIEGAND:")
            traceback.print_exc()
            