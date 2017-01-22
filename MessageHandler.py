"""
Wrap mosquito MQTT client and provide basic for receiving and sending data to MQTT broker
handle client and topics registrations
"""

import paho.mqtt.client as mqtt


class MessageHandler(object):
    def __init__(self, broker_addres, broker_port=1883, keep_alive=30):
        self.broker_address = broker_addres
        self.broker_port =broker_port
        self.keep_alive = keep_alive
        self.client = None
        self.is_connected = False

        self._connect()

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
    def _on_connect_callback(client, userdata, rc):
        if rc == 0:
            print("Succesfully connected to broker")
            # self.is_connected = True
        else:
            print("Connection error " + str(rc))

    @staticmethod
    def _on_disconnect_callback(userdata, rc):
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