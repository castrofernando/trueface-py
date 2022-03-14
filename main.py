#!/usr/bin/python3

from asyncio import events
import cv2
import time
from cv2 import trace
import numpy
import os
import sys
import imutils 
import logging
from threading import Thread
from flask import Flask, render_template, Response,jsonify, request
import requests
from functools import wraps
from vision_box_api import VisionBoxApi
import RPi.GPIO as GPIO
from config import TERMINAL_ID, VB_COLLECTION_ID, VB_NAMESPACE, VB_PASS, VB_PORT, VB_URL_BASE, VB_USERNAME, VB_VERSION, VB_ENABLE_SPOOF_DETECT,VB_IDENTIFY_THRESHOLD, VB_SPOOF_DETECT_THRESHOLD, WIEGAND_BITS,USE_FACILITY,ENABLE_WIEGAND,ENABLE_REMOTE_AUTH,REMOTE_AUTH_URL,CAMERA_TYPE,CAMERA_URL
from events import Events
from datetime import datetime
from wiegand import Wiegand
import pyzbar.pyzbar as pyzbar
import queue
import traceback
from auto_search import AutoSearch
import base64


check_auth = lambda username, password: username == 'username' and password == 'password'
jpeg = bytearray()
token = ''
startTime=0
authFinished=False
GPIO.setmode (GPIO.BOARD)
GPIO.setup (7,GPIO.OUT)
image_count=0
events = []
speed_queue = queue.Queue()

wiegandOut = Wiegand(11,12)
wiegandOut.send(121235,26,False)

broadcastServer = AutoSearch()

if not os.path.exists('static'):
    os.mkdir('static')

app = Flask(__name__)
vbApi = VisionBoxApi(url_base=VB_URL_BASE,port=VB_PORT,api_version=VB_VERSION,username=VB_USERNAME,password=VB_PASS)

def remoteAuthenticate(credential):
    try:
        with open("userimage.jpg", "rb") as image_file:
            encoded_imageb64 = base64.b64encode(image_file.read())
        payload = {
            "terminal_id": TERMINAL_ID,
            "credential": credential,
            "event_image": encoded_imageb64.decode('utf-8')
            }
        response = requests.post(url=REMOTE_AUTH_URL,json=payload)
        print(response)
        #TODO: DECODE RESPONSE FROM ACCESS CONTROL SYSTEM
        
    except Exception as e:
        print("ERRO_remoteAuthenticate:")
        traceback.print_exc() 


def decode_qrcode(im) : 
    global image_count

    hasDecodedObj=False
    execution_time=time.time()
    
    # Convert to grayscale
    img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # Find barcodes and QR codes
    decodedObjects = pyzbar.decode(img)
    execution_time=time.time()-execution_time
    # Print results
    for obj in decodedObjects:
        print('Type : ', obj.type)
        print('Data : ', obj.data,'\n')  
        if(ENABLE_WIEGAND):
            wiegandOut.send(int(obj.data.decode("utf-8")),WIEGAND_BITS,USE_FACILITY)
        if(ENABLE_REMOTE_AUTH):
            remoteAuthenticate(int(obj.data.decode("utf-8")))

        if(image_count<10):
            cv2.imwrite('static/user_{}.jpg'.format(image_count),im)
            now = datetime.now()
            data = Events(file_name='user_{}.jpg'.format(image_count),
                            name=str(obj.data.decode("utf-8")),
                            event_date=now.strftime("%d/%m/%Y %H:%M:%S"),
                            execution_time=execution_time)
            events.insert(image_count,data)
            image_count+=1
            hasDecodedObj=True
        else:
            image_count=0
            cv2.imwrite('static/user_{}.jpg'.format(image_count),im)
            now = datetime.now()
            data = Events(file_name='user_{}.jpg'.format(image_count),
                            name=str(obj.data.decode("utf-8")),
                            event_date=now.strftime("%d/%m/%Y %H:%M:%S"),
                            execution_time=execution_time)
            events.insert(image_count,data)
            image_count+=1
            hasDecodedObj=True
    return [hasDecodedObj,decodedObjects]

@app.route('/',methods=["GET"])
#@login_required
def index():
    global events
    #print(events[0])
    # rendering webpage
    return render_template('index.html', events=events)

@app.route('/reboot',methods=["GET"])
#@login_required
def reboot():
    global events
    #print(events[0])
    # rendering webpage
    os.system('sudo reboot')
    return render_template('index.html', events=events)


@app.route('/settings')
def settings():
    payload = {
        "VB_URL_BASE":VB_URL_BASE,
        "VB_PORT":VB_PORT,
        "VB_VERSION":VB_VERSION,
        "VB_USERNAME":VB_USERNAME,
        "VB_PASS":VB_PASS,

        #USER SETTINGS - VISION BOX
        "VB_IDENTIFY_THRESHOLD":VB_IDENTIFY_THRESHOLD,
        "VB_SPOOF_DETECT_THRESHOLD":VB_SPOOF_DETECT_THRESHOLD,
        "VB_ENABLE_SPOOF_DETECT":VB_ENABLE_SPOOF_DETECT,
        "VB_COLLECTION_ID":VB_COLLECTION_ID,
        "VB_NAMESPACE":VB_NAMESPACE,

        #wiegand settings 
        "ENABLE_WIEGAND":ENABLE_WIEGAND,
        "WIEGAND_BITS":WIEGAND_BITS,
        "USE_FACILITY":USE_FACILITY,

        #3rd party rest integration
        "ENABLE_REMOTE_AUTH":ENABLE_REMOTE_AUTH,
        "REMOTE_AUTH_URL":REMOTE_AUTH_URL,

        #UDP Broadcast
        "AUTO_SEARCH_PORT":32777
    }
    return jsonify(results = payload)

def programRunning(speed_queue):
    speed = 1
    while True:
        try:
            speed = speed_queue.get(timeout=.001)
            if speed == 0:
                break
        except queue.Empty:
            pass
        #print("speed:", speed)
        GPIO.output(7,1) 
        time.sleep(speed)
        GPIO.output(7,0)
        time.sleep(speed) 
        

def startCam():
    # Load the cascade
    global jpeg
    global startTime
    global authFinished
    global image_count
    global events
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if(CAMERA_TYPE!=0):
        cap = cv2.VideoCapture(CAMERA_URL,cv2.CAP_FFMPEG) #-> camera rtsp
        print('Connecting RTSP URI: ' + CAMERA_URL,file=sys.stdout)
    else:
        cap = cv2.VideoCapture(0) #uri da webcam -> 0
        print('Connecting WEBCAM 0',file=sys.stdout)
    
         # Test to see video size
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    
    print('size:'+repr(size),file=sys.stdout)

    while cap.isOpened():
        #this skip some frames
        cap.grab()
        ret, img = cap.read()
        if ret:
            #print("im ok")          
            
            #decode QRCode
            if(startTime<time.time()):
                ret, decodedObjects = decode_qrcode(img)
                if(ret):
                    startTime=time.time()+2
            
            #reduce image size to 0.6 * imageSize
            img=cv2.resize(img,None,fx=0.6,fy=0.6,interpolation=cv2.INTER_AREA)  
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect the faces
            faces = face_cascade.detectMultiScale(gray,scaleFactor=1.3, minNeighbors=3, minSize=(150,150),flags=cv2.CASCADE_SCALE_IMAGE)
            
            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.imwrite('userimage.jpg', img)
                if(startTime<time.time() and not (authFinished)):
                    speed_queue.put(.1)
                    img = cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)                    
                    execution_time=time.time()
                    vbApi.login()
                    result, name = vbApi.identify_person(namespace=VB_NAMESPACE,collection_id=VB_COLLECTION_ID)
                    startTime=int(time.time()) + 5
                    if(result):
                        if(VB_ENABLE_SPOOF_DETECT and vbApi.passive_detect_spoof()):
                            img = cv2.putText(img, str(name["predicted_label"]), (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                                                    1, (255, 0, 0), 2, cv2.LINE_AA) 
                            execution_time=time.time()-execution_time
                            print("AUTENTICATED IN {} SECONDS".format(execution_time),file=sys.stdout)
                            speed_queue.put(1)   
                            if(ENABLE_WIEGAND):
                                try:
                                    wiegandOut.send(int(str(name["predicted_label"])),WIEGAND_BITS,USE_FACILITY)
                                except Exception as e:
                                    traceback.print_exc()
                            if(ENABLE_REMOTE_AUTH):
                                remoteAuthenticate(str(name["predicted_label"]))
                            #GPIO.output(7,1) 
                            authFinished=True 
                            if(image_count<10):
                                cv2.imwrite('static/user_{}.jpg'.format(image_count),img)
                                now = datetime.now()
                                data = Events(file_name='user_{}.jpg'.format(image_count),
                                              name=str(name["predicted_label"]),
                                              event_date=now.strftime("%d/%m/%Y %H:%M:%S"),
                                              execution_time=execution_time)
                                events.insert(image_count,data)
                                image_count+=1
                            else:
                                image_count=0
                                cv2.imwrite('static/user_{}.jpg'.format(image_count),img)
                                now = datetime.now()
                                data = Events(file_name='user_{}.jpg'.format(image_count),
                                              name=str(name["predicted_label"]),
                                              event_date=now.strftime("%d/%m/%Y %H:%M:%S"),
                                              execution_time=execution_time)
                                events.insert(image_count,data)
                                image_count+=1
                    speed_queue.put(1)
            if(startTime<time.time() and authFinished):
                #GPIO.output(7,0)                    
                authFinished=False    
            
            # Display
            #cv2.imshow(str(cameraUri), img)
        else:
            #try reconnect camera
            print("Fail to read frames. Trying reconnect camera...",file=sys.stdout)
            attemps=0
            while(True):
                attemps+=1
                cap.release()
                time.sleep(5)
                if(CAMERA_TYPE!=0):
                    cap = cv2.VideoCapture(CAMERA_URL,cv2.CAP_FFMPEG) #-> camera rtsp
                    print('Connecting RTSP URI: ' + CAMERA_URL,file=sys.stdout)
                else:
                    cap = cv2.VideoCapture(0) #uri da webcam -> 0
                    print('Connecting WEBCAM 0',file=sys.stdout)
                if(cap.isOpened()):
                    ret, img = cap.read()
                    if(ret):
                        break
                else:
                    print("Fail to connect - Attemps: " + str(attemps),file=sys.stdout)

        k = cv2.waitKey(1) & 0xff
        if k==27:
            cap.release()
            cv2.destroyAllWindows()
            break
        elif k==ord('a'):
            cv2.imwrite('userimage.jpg', img)
            print("pressed a to exit",file=sys.stdout)

if __name__ == "__main__":

    cam1 = Thread(target=startCam)
    #cam2 = Thread(target=startCam,args=('0'))
    cam1.start()
    #cam2.start()
    
    led = Thread(target=programRunning,args=(speed_queue,))
    led.start()

    searchServer = Thread(target=broadcastServer.start_listening)
    searchServer.start()

    app.run(host='0.0.0.0',port='5000', debug=False)
    GPIO.cleanup()
    exit()
    
