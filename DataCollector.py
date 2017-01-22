"""
Handle incoming messages form ESP devices and sending data to Db layer
"""
from DatabaseAccess import *
import time
import json
from MessageHandler import MessageHandler


class DataCollector(object):
    def __init__(self, database_path, config_file):
        self.db = DatabaseAccess(database_path)
        self.topics = {"esp_hub/device/hello": self.new_device_callback,
          "esp_hub/device/+/telemetry": self.telemetry_callback,
          "esp_hub/device/+/data": self.data_callback}

        self.mqtt = MessageHandler('192.168.1.1')
        self.mqtt.register_topics(self.topics)

        while True:
            pass

    def extract_payload(self, msg):
        """
        Extract data msg from MQTT client
        :param msg: MQTT message
        :return: payload from device in json format
        """
        return json.loads(msg.payload.decode("utf-8"))

    def extract_device_id(self, msg):
        """
        Extract device id from topic string
        :param msg: MQTT message
        :return: device id
        """
        part = [i for i in msg.topic.split('/')]
        return part[part.index("device") + 1]

    def new_device_callback(self, client, userdata, msg):
        """
        Handle Hello msg from devices
        Topic: esp_hub/device/hello
        """
        data = self.extract_payload(msg)
        print(data["name"], data["id"])

        # device is in database
        if self.db.get_device(data['id']):
            reply = {"ip": "192.168.1.1", "port": 1883}
            self.mqtt.publish(str.format("esp_hub/device/{}/accept", data['id']), json.dumps(reply))
        else:
            self.verify_device(data['id'], data['name'], data['ability'])

    def telemetry_callback(self, client, userdata, msg):
        """
        Handle telemetry messages from devices
        Topic: esp_hub/device/+/telemetry
        """
        data = self.extract_payload(msg)

    def data_callback(self, client, userdata, msg):
        """
        Handle messages from device witch contain measured data
        Topic: esp_hub/device/+/data
        """
        data = self.extract_payload(msg)
        client_id = self.extract_device_id(msg)

        if 'type' in data and 'value' in data:
            record = DAO.Record(client_id, int(time.time()), data["type"], data["value"])
            self.db.insert_record(record)

    def verify_device(self, device_id, device_name, device_abilities):
        """
        Verifi device identitiy
        Blocking operation which wait for user response
        :param device_id:
        :param device_name:
        :param device_abilities:
        :return:
        """
        confirm = input(str.format("Do you want to add new device {} (ID: {})? [Y/n] ", device_name, device_id))
        if confirm.lower() == 'y' or confirm.lower() == 'yes':
            new_device = DAO.Device(device_id, device_name, device_abilities)
            self.db.insert_device(new_device)
            print("Add new device")
            reply = {"ip": "192.168.1.1", "port": 1883}
            self.mqtt.publish(str.format("esp_hub/device/{}/accept", device_id), json.dumps(reply))
