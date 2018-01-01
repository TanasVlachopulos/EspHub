import json
from Log import Log
from MqttHandler import MqttHandler
from Config import Config
import uuid
import time
import click

log = Log.get_logger()


class ImageTransmitter(object):
	BASE_REQUEST_TOPIC = "esp_hub/api/request/"
	BASE_RESPONSE_TOPIC = "esp_hub/api/response/"

	def __init__(self):
		self.mqtt = MqttHandler("tanas.eu")
		self.request_pool = set()
		self.response_pool = dict()

	def register_topic(self, topic):
		self.mqtt.register_topic(topic, self.mqtt_api_response_callback)

	def mqtt_api_response_callback(self, client, userdata, msg):
		response_id = msg.topic.split('/')[-1]
		if response_id in self.request_pool:
			self.request_pool.remove(response_id)
			log.debug("Incoming response on request {}.".format(response_id))

			try:
				response = json.loads(msg.payload.decode('utf-8'))
				self.response_pool[response_id] = response
			except ValueError:
				log.error("Cannot parse response from server.")
				self.response_pool[response_id] = None

		else:
			log.error("unknown response id")

	# def get_device_response_callback(self, payload):
	# 	# todo print output to console using click and return
	# 	response = {}
	# 	try:
	# 		response = json.loads(payload)
	# 	except ValueError:
	# 		log.error("Cannot parse response from server.")
	# 		return
	#
	# 	print("{:15}{:15}".format("device name", "device id"))
	# 	print("-" * 30)
	# 	for device in response.get('payload', list()):
	# 		print("{:15}{:15}".format(device.get('name'), device.get('id')))

	def wait_for_response(self, request_id):
		while request_id not in self.response_pool:
			time.sleep(0.1)

		return self.response_pool[request_id]


@click.group()
@click.option('-b', type=str, required=True)
@click.option('-p', type=int, default=1883)
@click.pass_context
def cli(ctx, b, p):
	print(b)
	ctx.obj = ImageTransmitter()

@cli.command("send-image")
@click.pass_obj
def send_image(it):
	"""

	:param it: Context to ImageTransmitter object
	:type it: ImageTransmitter
	:return:
	"""
	click.echo(it.BASE_REQUEST_TOPIC)

@cli.command("get-devices")
@click.pass_obj
def get_devices(it):
	"""
	Obtain list of display devices from EspHubServer over MQTT.
	:return:
	"""
	uid = str(uuid.uuid4())
	it.request_pool.add(uid)
	it.register_topic(it.BASE_RESPONSE_TOPIC + "+")
	it.mqtt.publish("{}{}".format(it.BASE_REQUEST_TOPIC, uid), "get_display_devices", qos=1)

	response = it.wait_for_response(uid)
	print("{:15}{:15}".format("device name", "device id"))
	print("-" * 30)
	for device in response.get('payload', list()):
		print("{:15}{:15}".format(device.get('name'), device.get('id')))

	return response

if __name__ == "__main__":
	# it = ImageTransmitter()
	# it.cli()
	# it.get_devices()
	cli()
