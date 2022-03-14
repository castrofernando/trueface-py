#VISIONBOX SERVER SETTINGS
VB_URL_BASE='http://192.168.15.7'
VB_PORT=8080
VB_VERSION='v1'
VB_USERNAME='fernando.castro@acess-e.com'
VB_PASS='guitar15'

#USER SETTINGS - VISION BOX
VB_IDENTIFY_THRESHOLD=0.3
VB_SPOOF_DETECT_THRESHOLD=0.6
VB_ENABLE_SPOOF_DETECT=True
VB_COLLECTION_ID='test'
VB_NAMESPACE='acesse'
CAMERA_TYPE=0 #0 -> Webcam / 1 -> RTSP
CAMERA_URL='rtsp://192.168.15.120/video.pro4' #this cam be ignored if used webcam

#wiegand settings 
TERMINAL_ID=1
ENABLE_WIEGAND=True
WIEGAND_BITS=26
USE_FACILITY=True

#3rd party rest integration
ENABLE_REMOTE_AUTH=True
REMOTE_AUTH_URL='https://trueface-test.requestcatcher.com/test'

#auto search port
AUTO_SEARCH_PORT=32777


