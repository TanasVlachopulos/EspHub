import json
from Log import Log
from MqttHandler import MqttHandler
from Config import Config
import uuid
import time
import click
from PIL import Image

log = Log.get_logger()


class ImageTransmitter(object):
	BASE_REQUEST_TOPIC = "esp_hub/api/request/"
	BASE_RESPONSE_TOPIC = "esp_hub/api/response/"

	def __init__(self, server_address, port):
		self.mqtt = MqttHandler(server_address, port)
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

	def wait_for_response(self, request_id):
		while request_id not in self.response_pool:
			time.sleep(0.1)

		return self.response_pool[request_id]

	def convert_bitmap_to_xbm_raw(self, bitmap_bytes):
		xbm_lst = []
		try:
			for i in range(0, len(bitmap_bytes), 8):
				# print(i, end=' ')
				pixel_byte = 0
				for bit in range(7, -1, -1):
					pixel_byte <<= 1
					pixel_byte |= bitmap_bytes[i + bit]

				xbm_lst.append(pixel_byte)
		except IndexError:
			print('end')

		return bytearray(xbm_lst)


@click.group()
@click.option('-b', '--broker', type=str, required=True)
@click.option('-p', '--port', type=int, default=1883)
@click.pass_context
def cli(ctx, broker, port):
	ctx.obj = ImageTransmitter(broker, port)


@cli.command("send-image")
@click.option('-d', '--device', type=str, required=True, help="Device ID or device name.")
@click.argument('bitmap', type=click.Path(exists=True, readable=True))
@click.pass_obj
def send_image(it, device, bitmap):
	"""

	:param it: Context to ImageTransmitter object
	:type it: ImageTransmitter
	:return:
	"""
	img = Image.open(bitmap)
	img_bytes = img.tobytes()
	xbm_bytes = it.convert_bitmap_to_xbm_raw(img_bytes)

	it.mqtt.publish("esp_hub/device/{}/display".format(device), xbm_bytes)


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
