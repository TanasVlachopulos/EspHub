"""
Aplication start point

"""
from DataCollector import DataCollector
from DatabaseAccess import *
from Commands import *
import time
from signal import signal
import json

from MessageHandler import MessageHandler

DataCollector("test.db", "conf")

# db = DatabaseAccess('test.db')


# device = DAO.Device('222:22:33:99:66:11', 'unknown_device', '10.10.0.1', ['temp', 'analog'])
# print(device.to_list())
# msg = ['@hello', '10.10.0.12', '222:22:33:99:66:11', 'test_device']
# func = command_dic[msg[0]]
# func(msg)
# msg = ["@provided_func", '222:22:33:99:66:11', 'analog', 'radiation']
# func = command_dic[msg[0]]
# func(msg)
# msg = ['@record', '222:22:33:99:66:11', 'analog', '3.33']
# func = command_dic[msg[0]]
# func(msg)
# db.insert_device(device)
# [print(x) for x in db.get_devices()]
# record = DAO.Record('66:22:33:99:66:111111', time.time(), 'temp', '32.2')
# db.insert_record(record)
# [print(x) for x in db.get_record_from_device('222:22:33:99:66:11')]


# def extract_payload(msg):
#     return json.loads(msg.payload.decode("utf-8"))
#
#
# def extract_device_id(msg):
#     part = [i for i in msg.topic.split('/')]
#     return part[part.index("device") + 1]
#
#
# def callback(client, userdata, msg):
#     print("Topic: " + msg.topic + " Message: " + str(msg.payload))
#     # print(msg)
#     # print(client)
#     # print(userdata)
#
#
# def new_device_callback(client, userdata, msg):
#     data = extract_payload(msg)
#     print(data["name"], data["id"])
#
#     # device is in database
#     if db.get_device(data['id']):
#         reply = {"ip": "192.168.1.1", "port": 1883}
#         mqtt.publish(str.format("esp_hub/device/{}/accept", data['id']), json.dumps(reply))
#     else:
#         verify_device(data['id'], data['name'], data['ability'])
#
#
# def telemetry_callback(client, userdata, msg):
#     data = extract_payload(msg)
#     # print(data)
#     # print(extract_device_id(msg))
#
#
# def data_callback(client, userdata, msg):
#     data = extract_payload(msg)
#     client_id = extract_device_id(msg)
#
#     if 'type' in data and 'value' in data:
#         record = DAO.Record(client_id, int(time.time()), data["type"], data["value"])
#         db.insert_record(record)
#
#
# def verify_device(device_id, device_name, device_abilities):
#     confirm = input(str.format("Do you want to add new device {} (ID: {})? [Y/n] ", device_name, device_id))
#     if confirm.lower() == 'y' or confirm.lower() == 'yes':
#         new_device = DAO.Device(device_id, device_name, device_abilities)
#         db.insert_device(new_device)
#         print("Add new device")
#         reply = {"ip": "192.168.1.1", "port": 1883}
#         mqtt.publish(str.format("esp_hub/device/{}/accept", device_id), json.dumps(reply))
#
#
# mqtt = MessageHandler('192.168.1.1')
# # mqtt.register_topic("esp_hub/device/hello", new_device_callback)
# # mqtt.register_topic("esp_hub/device/+/telemetry", telemetry_callback)
#
# topics = {"esp_hub/device/hello": new_device_callback,
#           "esp_hub/device/+/telemetry": telemetry_callback,
#           "esp_hub/device/+/data": data_callback}
#
# mqtt.register_topics(topics)
#
# while True:
#     pass
