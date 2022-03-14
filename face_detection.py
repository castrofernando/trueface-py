import cv2
import time
import numpy
import os
import imutils 
import logging
from threading import Thread

def startCam(cameraUri,camType):
    # Load the cascade
    os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if(camType!='webcam'):
        cap = cv2.VideoCapture(cameraUri)
    else:
        cap = cv2.VideoCapture(0)
    
         # Test to see video size
    size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    
    print('Connecting URI: ' + str(cameraUri))
    print('size:'+repr(size))


    while cap.isOpened():
        #this skip some frames
        cap.grab()
        ret, img = cap.read()
        if ret:
            #print("im ok")
            img=cv2.resize(img,None,fx=0.6,fy=0.6,interpolation=cv2.INTER_AREA)                    
            # Convert to grayscale
                        
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Detect the faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 3)
            # Draw the rectangle around each face
            for (x, y, w, h) in faces:
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
                image = cv2.putText(img, str(len(faces)), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (255, 0, 0), 2, cv2.LINE_AA)              
            # Display
            cv2.imshow(str(cameraUri), img)
        #else:
            #print("im not ok")
        k = cv2.waitKey(1) & 0xff
        if k==27:
            cap.release()
            cv2.destroyAllWindows()
            break
        elif k==ord('a'):
            cv2.imwrite('img.jpg', img)
            print("pressed a")

if __name__ == "__main__":

    #cam1 = Thread(target=startCam,args=('rtsp://192.168.15.120/video.pro4',cv2.CAP_FFMPEG))
    
    cam2 = Thread(target=startCam,args=(0,'webcam'))
    #cam1.start()
    cam2.start()
    while True:
        time.sleep(1)
        pass
    # Release the VideoCapture object
