"""
Send broadcast discovery message to devices
"""

import json
import socket
import threading
import time


class EspDiscovery(threading.Thread):
    def __init__(self, address, port, msg, interval):
        threading.Thread.__init__(self)
        self.address = address
        self.port = port
        self.msg = msg
        self.interval = interval
        self.udp_soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        ### Multicast does not work on Windows due to magic windows firewall
        # self.udp_soc.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)  # for multicast
        self.udp_soc.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # for broadcast

    def run(self):
        while True:
            self.udp_soc.sendto(self.msg.encode('utf-8'), (self.address, self.port))
            print("Request send ...")
            time.sleep(self.interval)

        print('End Transmission')


msg = json.dumps({"name": "testServer", "ip": "192.168.1.1", "port": 1883})

esp_discovery = EspDiscovery('192.168.1.255', 11114, msg, 5)
esp_discovery.start()


