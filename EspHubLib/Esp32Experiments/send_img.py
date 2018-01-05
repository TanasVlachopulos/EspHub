import os
import paho.mqtt.client as mqtt
import socket
import json
import logging
import uuid
import time
import sys
from PIL import Image

class Log(object):
    logger = None

    def __init__(self):
        """
        Init logger to console and file in library home directory.
        Log has should have only one instance, so call get_logger method instead of constructor.
        """

        path = os.path.join('', 'esp_hub_unilib.log')

        log = logging.getLogger("EspHubUnilib")
        log.setLevel(logging.DEBUG)
        lh = logging.FileHandler(path)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        log.addHandler(ch)
        lh.setLevel(logging.DEBUG)
        lh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
        log.addHandler(lh)
        Log.logger = log

    @staticmethod
    def get_logger():
        if not Log.logger:
            Log()
            return Log.logger
        else:
            return Log.logger


class MqttHandler(object):
    def __init__(self, broker_addres, broker_port=1883, keep_alive=30, client_id="", username="", password=""):
        """
        Handle connection to MQTT broker
        :param broker_addres:
        :param broker_port:
        :param keep_alive:
        :param client_id:
        :param username:
        :param password:
        """
        self.broker_address = broker_addres
        self.broker_port = broker_port
        self.keep_alive = keep_alive
        self.client = None
        self.client_id = client_id
        self.is_connected = False
        self.log = Log.get_logger()

        try:
            self._connect(client_id, username, password)
        except ConnectionRefusedError:
            self.log.error("Cannot connetct to MQTT broker")

    def _connect(self, client_id, username, password):
        self.client = mqtt.Client(client_id=client_id)
        self.client.on_connect = self._on_connect_callback
        self.client.on_disconnect = self._on_disconnect_callback

        try:
            self.client.connect(self.broker_address,
                                self.broker_port, self.keep_alive)
            self.is_connected = True
        except TimeoutError:
            self.log.error(
                "Connection timeout. Remote MQTT broker is currently unavailable. Check whether the broker is running.")
            self.is_connected = False

        self.client.loop_start()

    def _on_connect_callback(self, client, userdata, flags, rc):
        if rc == 0:
            self.log.info("Successfully connected to MQTT broker")
            self.is_connected = True

    def _on_disconnect_callback(self, client, userdata, rc):
        self.log.warning("Disconnected from MQTT broker")
        self.is_connected = False

    def register_topic(self, topic, callback, qos=1):
        """
        Register specific topic for subscription
        :param topic: Subscribed topic
        :param callback: Callback function with signature (client, userdata, msg)
        :param qos: Qos level (default 1)
        :return:
        """
        if self.client and self.is_connected:
            self.client.subscribe(topic, qos=qos)
            self.client.message_callback_add(topic, callback)

    def publish(self, topic, payload, qos=1, retain=False):
        """
        Wrap MQTT publish
        :param topic: Message topic
        :param payload: Message content
        :param qos: Message QOS (default 0)
        :param retain: Is retain message (default false)
        :return: if client is connected True, if disconnected False
        """
        if self.client and self.is_connected:
            res = self.client.publish(topic, payload, qos=qos, retain=retain)
            res.wait_for_publish()
            return True
        else:
            self.log.error(
                "Cannot publish message, MQTT client is disconnected")
            return False


def convert_bitmap_to_xbm_raw(bitmap_bytes):
    xbm_lst = []
    try:
        for i in range(0, len(bitmap_bytes), 8):
            # print(i, end=' ')
            pixel_byte = 0
            for bit in range(7, -1, -1):
                pixel_byte <<= 1
                pixel_byte |= bitmap_bytes[i + bit]
                # print(i+bit, end=' ')
            # print('0x{:02X},'.format(pixel_byte), end=' ')
            xbm_lst.append(pixel_byte)
    except IndexError: 
        print('end')

    return xbm_lst

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Error: missing some arguments.")
        sys.exit(1)

    mqh = MqttHandler(sys.argv[1])
    
    img = Image.open(sys.argv[2])
    img_bytes = img.tobytes()
    print('Len of img bytes:', len(img_bytes))
    
    b_list_out = convert_bitmap_to_xbm_raw(img_bytes)
    print(b_list_out)

    b_out = bytearray(b_list_out)
    print(b_out)
    print(len(b_out))
    # print(img_bytes)

    esps = ['564440624', '950316592']

    for esp in esps:
        # print(img_bytes)
        mqh.publish("esp_hub/device/{}/display".format(esp), b_out)
        time.sleep(1)
