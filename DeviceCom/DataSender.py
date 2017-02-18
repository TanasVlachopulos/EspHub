from .MessageHandler import MessageHandler
import json
from Config import Config

conf = Config.Config().get_config()


class _DataSender(object):
    def __init__(self):
        self.mqtt = MessageHandler(conf.get('mqtt', 'ip'), conf.getint('mqtt', 'port'))

    def verify_device(self, device_id):
        reply = {"ip": conf.get('mqtt', 'ip'), "port": conf.getint('mqtt', 'port')}
        self.mqtt.publish(str.format("esp_hub/device/{}/accept", device_id), json.dumps(reply), qos=1)

    def send_data_to_device(self, device_id, value_type, value, default_value=0):
        reply = {"type": value_type, "value": value, "dvalue": default_value}
        self.mqtt.publish(str.format("esp_hub/device/{}/data", device_id), json.dumps(reply), qos=1)


class Singleton(type):
    """ Singleton meta class """
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class DataSender(_DataSender, metaclass=Singleton):
    """ Empty class inherit from _Dba class with meta property Singleton """
    pass
