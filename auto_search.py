from inspect import isroutine
import socket
import json
import psutil
from config import AUTO_SEARCH_PORT
import traceback

class AutoSearch:

    def __init__(self) -> None:
        self.hostname = socket.gethostname()
        self.serverUdp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        self.serverUdp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.isRunning=True

        # Enable broadcasting mode
        try:
            self.serverUdp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self.serverUdp.bind(("", AUTO_SEARCH_PORT))
        except:
            print("ERRO_BIND_AUTOSEARCH:")
            traceback.print_exc()
        pass

    def get_ip_addresses(self,family):
        self.hostname = socket.gethostname()

        for interface, snics in psutil.net_if_addrs().items():
            for snic in snics:
                if snic.family == family:
                    yield (interface, snic.address)


    def start_listening(self):
        try:
            while self.isRunning:
                # Thanks @seym45 for a fix
                data, addr = self.serverUdp.recvfrom(1024)
                if(data.decode('utf-8')=='$TRUEFACE-BROADCAST-AUTOSEARCH$'):
                    print("received message: %s"%data)
                    ipv4s = list(self.get_ip_addresses(socket.AF_INET))
                    ips = ''
                    for i in ipv4s:
                        print(i[1])
                        ips+=i[1]+','
                    data = {
                        "ip": ips[:-1],
                        "hostname": self.hostname
                    }
                    self.serverUdp.sendto(bytes(json.dumps(data), "utf-8"),('255.255.255.255',AUTO_SEARCH_PORT))
        except Exception as e:
            print("ERRO_start_listening_udp:")
            traceback.print_exc()

        