import serial
import time
import RPi.GPIO as GPIO
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
i  = 0
v1 = 0
v2 = 0
v3 = 0
v4 = 0
vt = 0
t1 = 0
t2 = 0
t3 = 0
t4 = 0
t5 = 0

# Use the application default credentials
cred = credentials.Certificate('./ServiceAccountKey.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

iRef = db.collection(u'SensorData').document(u'Current')
vRef = db.collection(u'SensorData').document(u'Voltages')
tRef = db.collection(u'SensorData').document(u'Temperatures')
socRef = db.collection(u'SensorData').document(u'SOC')

ser = serial.Serial('/dev/ttyUSB1', 9600)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # switch
GPIO.add_event_detect(8, GPIO.RISING, bouncetime = 500)
GPIO.setup(12, GPIO.OUT) # relay1 -ve
GPIO.setup(16, GPIO.OUT) # relay2 pre charge relay
GPIO.setup(18, GPIO.OUT) # relay3_discharge +ve
GPIO.setup(22, GPIO.OUT) # relay4_charging +ve
GPIO.setup(24, GPIO.OUT) # fan
GPIO.output(12, GPIO.LOW)
GPIO.output(16, GPIO.LOW)
GPIO.output(18, GPIO.LOW)
GPIO.output(22, GPIO.LOW)
GPIO.output(24, GPIO.LOW)

switch = False
reset = False

while True:
    if GPIO.event_detected(8):
        if switch == False:
            switch = True
        else:
            switch = False
    
    if switch == True:
        #switch on
        GPIO.output(12, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(16, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(18, GPIO.HIGH)
            
    else:
        #switch off
        GPIO.output(18, GPIO.LOW)
        GPIO.output(12, GPIO.LOW)
        GPIO.output(16, GPIO.LOW)
        
        
    if(ser.in_waiting > 0):
         for k in range(11):
            arduinoData = ser.readline().decode('utf-8').strip()
            print(arduinoData)
            
            if k == 0:
                with open ("i.txt", "a") as _i:
                    _i.write(arduinoData + '\n')
                i = float(arduinoData)
                iRef.update({u'Current': i})
            
            elif k == 1:
                with open ("v1.txt", "a") as _v1:
                    _v1.write(arduinoData + '\n')
                v1 = float(arduinoData)
                vRef.update({u'Voltage1': v1})
                
            elif k == 2:
                with open ("v2.txt", "a") as _v2:
                    _v2.write(arduinoData + '\n')
                v2 = float(arduinoData)
                vRef.update({u'Voltage2': v2})
                
            elif k == 3:
                with open ("v3.txt", "a") as _v3:
                    _v3.write(arduinoData + '\n')
                v3 = float(arduinoData)
                vRef.update({u'Voltage3': v3})
            
            elif k == 4:
                with open ("v4.txt", "a") as _v4:
                    _v4.write(arduinoData + '\n')
                v4 = float(arduinoData)
                vRef.update({u'Voltage4': v4})
                
            elif k == 5:
                with open ("vt.txt", "a") as _vt:
                    _vt.write(arduinoData + '\n')
                vt = float(arduinoData)
                vRef.update({u'VoltageT': vt})
                                
            elif k == 6:
                with open ("t1.txt", "a") as _t1:
                    _t1.write(arduinoData + '\n')
                t1 = float(arduinoData)
                tRef.update({u'Temperature1': t1})
                
            elif k == 7:
                with open ("t2.txt", "a") as _t2:
                    _t2.write(arduinoData + '\n')
                t2 = float(arduinoData)
                tRef.update({u'Temperature2': t2})
                
            elif k == 8:
                with open ("t3.txt", "a") as _t3:
                    _t3.write(arduinoData + '\n')
                t3 = float(arduinoData)
                tRef.update({u'Temperature3': t3})
                
            elif k == 9:
                with open ("t4.txt", "a") as _t4:
                    _t4.write(arduinoData + '\n')
                t4 = float(arduinoData)
                tRef.update({u'Temperature4': t4})
                
            elif k == 10:
                with open ("t5.txt", "a") as _t5:
                    _t5.write(arduinoData + '\n')
                t5 = float(arduinoData)
                tRef.update({u'Temperature5': t5})
    
    #Protection code
    #over current, over-voltage, under-volage, shortcircuit protection for both groups and pack
    if i > 100 or vt > 16.8 or v1 > 4.2 or v2 > 4.2 or v3 > 4.2 or v4 > 4.2:
        #switch off
        GPIO.output(18, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(16, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(12, GPIO.LOW)
        time.sleep(0.5)
        GPIO.output(22, GPIO.LOW)
        switch = False
        
    if vt <= 10 or v1 <= 2.5 or v2 <= 2.5 or v3 <= 2.5 or v4 <= 2.5:         
        #signal to start charging
        GPIO.output(18, GPIO.LOW)
        time.sleep(1)
        GPIO.output(22, GPIO.HIGH)
            
            
    #Cooling fan operation
    if t1 > 50 or t2 > 50 or t3 > 50 or t4 > 50 or t5 > 50:
        #signal to switch on fan
        GPIO.output(24, GPIO.HIGH)
    elif t1 < 50 or t2 < 50 or t3 < 50 or t4 < 50 or t5 < 50:
        #signal to switch off fan
        GPIO.output(22, GPIO.LOW)