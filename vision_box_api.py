import requests
import traceback

token = ''

class VisionBoxApi:

    def __init__(self,url_base,port,api_version,username,password,debug=False):
        self.url_base = url_base
        self.port = port
        self.username = username
        self.password = password
        self.api_version = api_version
        self.debug=debug

    def login(self):
        global token
        login = {
            "email": self.username,
            "password": self.password
        }
        uri = '{uri}:{port}/{version}/login'.format(uri=self.url_base, port=self.port, version=self.api_version)
        try:
            r = requests.post(url = uri,json = login)
            response = r.json()
            print(response["data"]["access_token"])
            token = response["data"]["access_token"]
            return token
        except Exception as e:
            print("ERRO_LOGIN:")
            traceback.print_exc()
    
    def identify_person(self,namespace,collection_id,threshold=0.3,num_candidates=3):
        global token
        uri = '{uri}:{port}/{version}/identify'.format(uri=self.url_base, port=self.port, version=self.api_version)

        headers = { "Accept" : "*/*",
                    "Authorization":"Bearer "+str(token) }

        payload={"collection_id": collection_id,
                    "namespace": namespace,
                    "threshold": threshold,
                    "num_candidates": num_candidates}
        files=[("source",("userimage.jpg",open("userimage.jpg","rb"),"image/jpeg"))]            
    
        try:
            response = requests.post(uri, headers=headers, data=payload, files=files)
            print(response.json())
            if(response.json()["success"]==True):
                return [True, response.json()["data"]["candidates"][0]]
            else:
                return [False,[]]
        except Exception as e:
            print("ERRO_IDENTIFY_PERSON:")
            traceback.print_exc()
            return [False,[]]

    def passive_detect_spoof(self, threshold=0.6):
        global token
        uri = '{uri}:{port}/{version}/spdetect'.format(uri=self.url_base, port=self.port, version=self.api_version)

        headers = { "Accept" : "*/*",
                    "Authorization":"Bearer "+str(token) }

        payload={"threshold": threshold}
        files=[("source",("userimage.jpg",open("userimage.jpg","rb"),"image/jpeg"))]            
    
        try:
            response = requests.post(uri, headers=headers, data=payload, files=files)
            print(response.json())
            if(response.json()["data"]["prediction"]=="fake"):
                return False
            else:
                return True
        except Exception as e:
            print("ERRO_PASSIVE_DETECT_SPOOF:")
            traceback.print_exc()
            return False
