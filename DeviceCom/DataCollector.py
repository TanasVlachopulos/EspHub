"""
Handle incoming messages form ESP devices and sending data to Db layer
"""
from datetime import datetime
import json
from DataAccess import DAO, DBA
from .MessageHandler import MessageHandler
from Config import Config

conf = Config.Config().get_config()


class DataCollector(object):
    def __init__(self, database_path, config_file):
        self.db = DBA.Dba(conf.get('db', 'path'))
        self.topics = {"esp_hub/device/hello": self.new_device_callback,
                       "esp_hub/device/+/telemetry": self.telemetry_callback,
                       "esp_hub/device/+/data": self.data_callback}

        self.mqtt = MessageHandler(conf.get('mqtt', 'ip'), conf.getint('mqtt', 'port'))
        self.mqtt.register_topics(self.topics)

    @staticmethod
    def extract_payload(msg):
        """
        Extract data msg from MQTT client
        :param msg: MQTT message
        :return: payload from device in json format
        """
        return json.loads(msg.payload.decode("utf-8"))

    @staticmethod
    def extract_device_id(msg):
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
            reply = {"ip": conf.get('mqtt', 'ip'), "port": conf.getint('mqtt', 'port')}
            self.mqtt.publish(str.format("esp_hub/device/{}/accept", data['id']), json.dumps(reply))
            # TODO load MQTT strings from config file
        else:
            provided_func = data['ability']
            provided_func = provided_func.replace('[', '')
            provided_func = provided_func.replace(']', '')
            provided_func = provided_func.replace(';', ',')
            provided_func = provided_func.replace(' ', '')
            provided_func = provided_func.replace('"', '')
            provided_func = provided_func.replace("'", '')
            provided_func = provided_func.split(',')
            # add device to waiting device list
            self.db.add_waiting_device(DAO.Device(data['id'], data['name'], provided_func))
            print(self.db)
            # self.verify_device(data['id'], data['name'], data['ability'])

    def telemetry_callback(self, client, userdata, msg):
        """
        Handle telemetry messages from devices
        Topic: esp_hub/device/+/telemetry
        """
        data = self.extract_payload(msg)
        device_id = self.extract_device_id(msg)

        print(data)
        telemetry = DAO.Telemetry(device_id, datetime.now(), rssi=data.get('rssi', '0'), heap=data.get('heap', '0'),
                                  cycles=data.get('cycles', '0'), ip=data.get('local_ip', '0'), mac=data.get('mac', '0'),
                                  voltage=data.get('voltage', '0'), ssid=data.get('ssid', '0'))
        self.db.insert_telemetry(telemetry)

    def data_callback(self, client, userdata, msg):
        """
        Handle messages from device witch contain measured data
        Topic: esp_hub/device/+/data
        """
        data = self.extract_payload(msg)
        client_id = self.extract_device_id(msg)

        if 'type' in data and 'value' in data:
            record = DAO.Record(client_id, datetime.now(), data["type"], data["value"])
            self.db.insert_record(record)
            print(">>> ", data['type'], data['value'])

    # obsolete - verification process ensures web application and Data sender
    # def verify_device(self, device_id, device_name, device_abilities):
    #     """
    #     Verifi device identitiy
    #     Blocking operation which wait for user response
    #     :param device_id:
    #     :param device_name:
    #     :param device_abilities:
    #     :return:
    #     """
    #     confirm = input(str.format("Do you want to add new device {} (ID: {})? [Y/n] ", device_name, device_id))
    #     if confirm.lower() == 'y' or confirm.lower() == 'yes':
    #         new_device = DAO.Device(device_id, device_name, device_abilities)
    #         self.db.insert_device(new_device)
    #         print("Add new device")
    #         reply = {"ip": "192.168.1.1", "port": 1883}
    #         self.mqtt.publish(str.format("esp_hub/device/{}/accept", device_id), json.dumps(reply))
