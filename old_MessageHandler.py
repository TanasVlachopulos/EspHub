import threading
import paho.mqtt.client as mqtt


class MessageHandler(threading.Thread):
    def __init__(self, broker_address, broker_port, keepalive):
        threading.Thread.__init__(self)

        self.broker_address = broker_address
        self.broker_port = broker_port
        self.keepalive= keepalive
        self.client = None

    def run(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        try:
            self.client.connect(self.broker_address, port=self.broker_port, keepalive=self.keepalive)
        except TimeoutError:
            print("Connection timeout. Remote MQTT broker is currently unavailable. Check whether the broker is running.")
            exit(0)

        self.client.loop_forever()

    @staticmethod
    def on_connect(client, userdata, rc):
        if rc == 0:
            print("Successfully connected to broker")
        else:
            print("connection error")

        client.subscribe("#")

    @staticmethod
    def on_message(client, userdata, msg):
        print("Topic: " + msg.topic + " Message: " + str(msg.payload))


handler_thread = MessageHandler("192.168.1.1", 1883, 30)
handler_thread.start()