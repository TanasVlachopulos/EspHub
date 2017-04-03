"""
Wrap mosquito MQTT client and provide basic for receiving and sending data to MQTT broker
handle client and topics registrations
"""

from Config import Config
import paho.mqtt.client as mqtt

conf = Config.Config().get_config()


class _MessageHandler(object):
    def __init__(self, broker_addres, broker_port=1883, keep_alive=30):
        self.broker_address = broker_addres
        self.broker_port =broker_port
        self.keep_alive = keep_alive
        self.client = None
        self.is_connected = False

        try:
            self._connect()
        except ConnectionRefusedError:
            print(conf.get('msg', 'mqtt_error'))

    def _connect(self):
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect_callback
        self.client.on_disconnect = self._on_disconnect_callback

        try:
            self.client.connect(self.broker_address, self.broker_port, self.keep_alive)
            self.is_connected = True  # test only

        except TimeoutError:
            print("Connection timeout. Remote MQTT broker is currently unavailable. Check whether the broker is running.")
            exit(0)

        self.client.loop_start()

    @staticmethod
    def _on_connect_callback(client, userdata, flags, rc):
        if rc == 0:
            print("Succesfully connected to broker")
            # self.is_connected = True
        else:
            print("Connection error " + str(rc))

    @staticmethod
    def _on_disconnect_callback(client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection")
        # self.is_connected = False

    def register_topic(self, topic, callback, qos=0):
        if self.client and self.is_connected:
            self.client.subscribe(topic, qos=qos)
            self.client.message_callback_add(topic, callback)

    def register_topics(self, topics):
        for topic, callback in topics.items():
            self.register_topic(topic, callback)

    def publish(self, topic, payload, qos=0, retain=False):
        self.client.publish(topic, payload, qos=qos, retain=retain)


class Singleton(type):
    _instance = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instance:
            cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instance[cls]


class MessageHandler(_MessageHandler, metaclass=Singleton):
    pass