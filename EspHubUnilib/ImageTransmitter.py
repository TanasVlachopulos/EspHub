from Log import Log
from MqttHandler import MqttHandler
from Config import Config
import uuid

class ImageTransmitter(object):
	def __init__(self):
		self.mqtt = MqttHandler("tanas.eu")
		self.mqtt.register_topic("esp_hub/api/response/+", self.mqtt_api_response_callback)
		self.request_queue = {}


	def mqtt_api_response_callback(self, client, userdata, msg):
		print(msg.payload.decode('utf-8'))
		# todo decode and send to get_device_response_callback

	def get_devices(self):
		"""
		Obtain list of display devices from EspHubServer over MQTT.
		:return:
		"""
		uid = str(uuid.uuid4())
		self.request_queue[uid] = self.get_device_response_callback
		self.mqtt.publish("esp_hub/api/request/{}".format(uid), "get_display_devices", qos=1)

		# TODO wait for response

	def get_device_response_callback(self, payload):
		# todo print output to console using click and return
		pass


if __name__ == "__main__":
	it = ImageTransmitter()

	it.get_devices()