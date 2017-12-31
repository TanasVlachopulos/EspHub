import json

from Log import Log
from MqttHandler import MqttHandler
from Config import Config
import uuid
import time

log = Log.get_logger()


class ImageTransmitter(object):
	def __init__(self):
		self.mqtt = MqttHandler("tanas.eu")
		self.mqtt.register_topic("esp_hub/api/response/+", self.mqtt_api_response_callback)
		self.request_queue = {}

	def mqtt_api_response_callback(self, client, userdata, msg):
		response_id = msg.topic.split('/')[-1]
		if response_id in self.request_queue:
			response_callback = self.request_queue[response_id]
			self.request_queue.pop(response_id)
			response_callback(msg.payload.decode('utf-8'))
		else:
			print("unknown response id")

	def get_devices(self):
		"""
		Obtain list of display devices from EspHubServer over MQTT.
		:return:
		"""
		uid = str(uuid.uuid4())
		self.request_queue[uid] = self.get_device_response_callback
		self.mqtt.publish("esp_hub/api/request/{}".format(uid), "get_display_devices", qos=1)

		while uid in self.request_queue:
			time.sleep(0.1)

	def get_device_response_callback(self, payload):
		# todo print output to console using click and return
		response = {}
		try:
			response = json.loads(payload)
		except ValueError:
			log.error("Cannot parse response from server.")
			return

		print("{:15}{:15}".format("device name", "device id"))
		print("-"*30)
		for device in response.get('payload', list()):
			print("{:15}{:15}".format(device.get('name'), device.get('id')))



if __name__ == "__main__":
	it = ImageTransmitter()

	it.get_devices()
