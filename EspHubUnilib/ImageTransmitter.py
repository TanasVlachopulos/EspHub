from PIL import Image
from Log import Log
from MqttHandler import MqttHandler
from threading import Event
from Config import Config
import uuid
import time
import click
import os
import json
import io

log = Log.get_logger()


class ImageTransmitter(object):
	BASE_REQUEST_TOPIC = "esp_hub/api/request/"
	BASE_RESPONSE_TOPIC = "esp_hub/api/response/"

	def __init__(self, server_address, port=1883, user_name="", password="", client_id=""):
		self.mqtt = MqttHandler(server_address, port, username=user_name, password=password, client_id=client_id)
		self.request_pool = dict()
		self.response_pool = dict()

	def register_topic(self, topic):
		"""
		Register specific topic.
		:param topic: Topic string.
		"""
		self.mqtt.register_topic(topic, self.mqtt_api_response_callback)

	def register_request(self):
		"""
		Generate and register request ID.
		:return: Unique request ID.
		"""
		uid = str(uuid.uuid4())
		self.request_pool[uid] = Event()  # create new waiting event default se to False
		return uid

	def mqtt_api_response_callback(self, client, userdata, msg):
		"""
		Callback for incoming responses from server.
		"""
		response_id = msg.topic.split('/')[-1]
		if response_id in self.request_pool:
			log.debug("Incoming response on request {}.".format(response_id))

			try:
				response = json.loads(msg.payload.decode('utf-8'))
				self.response_pool[response_id] = response
			except ValueError:
				log.error("Cannot parse response from server.")
				self.response_pool[response_id] = None

			event = self.request_pool[response_id]
			event.set()

		else:
			log.error("unknown response id")

	def wait_for_response(self, request_id, timeout=5):
		"""
		Check if request with given request_id receive response from server.
		Return server response if is available otherwise block program and wait for response.
		:param request_id: ID of request.
		:param timeout: Waiting timeout in seconds.
		:return: Response object dictionary.
		"""
		if request_id in self.request_pool:
			event = self.request_pool[request_id]
			if event.wait(timeout):
				return self.response_pool.pop(request_id)
			else:
				log.error("Request '{}' timeout. EspHubServer is probably unavailable.".format(request_id))
				return None

	@staticmethod
	def convert_image_to_bytes(bitmap_file, normalize=False):
		"""
		Load image file and convert it into universal bytes format.
		:param bitmap_file: Path to file or File object.
		:return: Image bytes
		"""
		img = None
		try:
			img = Image.open(bitmap_file)
		except OSError as e:
			log.error("Invalid input file.")
			log.error(e)
			return None

		if normalize:
			if img.mode == "RGBA":
				# replace alpha channel with white color
				img_data = img.load()
				for y in range(img.size[1]):
					for x in range(img.size[0]):
						if img_data[x, y][3] < 255:
							img_data[x, y] = (255, 255, 255, 255)
			# img.thumbnail([img.width, img.height], Image.ANTIALIAS)

			img = img.convert('L')  # convert image to monochrome (white = 0xff, black = 0x00)
			img_data = img.load()
			for y in range(img.size[1]):
				for x in range(img.size[0]):
					img_data[x, y] &= 1  # convert to 1 bit length 0xff -> 0x01, 0x00 -> 0x00
					img_data[x, y] ^= 1  # negate image bits

		return img.tobytes()

	def convert_bitmap_to_xbm_raw(self, bitmap_bytes):
		"""
		Convert monochrome bitmap with 1-bit color depth into 8px per byte monochrome format.
		:param bitmap_bytes: Bytes of bitmap in format '0x00 0x01 0x00 0x01 ...'
		:return: Bytearray with 8 pixels per byte.
		"""
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

	@staticmethod
	def get_display_topic(device_id):
		"""
		Provide topic for device display.
		:param device_id: Device ID.
		:return: Display topic.
		"""
		return "esp_hub/device/{}/display".format(device_id)

	@staticmethod
	def get_request_topic(uuid):
		"""
		Provide topic for MQTT api request.
		:param uuid: Unique request ID.
		:return: Request topic.
		"""
		return "{}{}".format(ImageTransmitter.BASE_REQUEST_TOPIC, uuid)


@click.group()
@click.option('-b', '--broker', type=str, required=True, help="MQTT broker domain name or IP address.")
@click.option('-p', '--port', type=int, default=1883, help="Network port of MQTT broker. Default 1883.")
@click.option('-u', '--user-name', type=str, default="", help="User name for connection to MQTT broker.")
@click.option('-P', '--password', type=str, default="", help="Password for connection to MQTT broker.")
@click.option('--client-id', type=str, default="", help="Specific client ID for connection to MQTT broker.")
@click.option('-v', '--verbose', is_flag=True, default=False, help="Enable debug outputs.")
@click.pass_context
def cli(ctx, broker, port, user_name, password, client_id, verbose):
	"""
	This multi-tool provides several methods to send data to a devices which use EspHubLibrary. The MQTT protocol is used for data transmission so running MQTT broker is required.
	"""
	if verbose:
		log.setLevel("DEBUG")
	else:
		log.setLevel("INFO")

	ctx.obj = ImageTransmitter(broker, port=port, user_name=user_name, password=password, client_id=client_id)
	ctx.obj.register_topic(ctx.obj.BASE_RESPONSE_TOPIC + "+")


@cli.command("send-image")
@click.option('-d', '--device', type=str, required=True, help="Device ID or device name.")
@click.option('--normalize/--no-normalize', default=True, help="Normalize image to monochrome format. Default Enabled.")
@click.argument('bitmap', type=click.Path(exists=True, readable=True))
@click.pass_obj
def send_image(it, device, normalize, bitmap):
	"""
	Send single image to specific device.

	Recommended format is monochrome .bmp with 1-bit color depth but also other format such as .png can be used if normalize option is enabled.
	Normalization process try to convert image into standardized monochrome format but quality of results is questionable.
	"""
	if not os.path.isfile(bitmap):
		log.error("Given path '{}' is not a file.".format(bitmap))
		return

	device_id = translate_device_name(it, device)
	if not device_id:
		return

	bytes = it.convert_image_to_bytes(bitmap, normalize=normalize)
	if bytes:
		xbm_bytes = it.convert_bitmap_to_xbm_raw(bytes)
		it.mqtt.publish(it.get_display_topic(device_id), xbm_bytes, qos=0)
		log.info("Image '{}' successfully send.".format(bitmap))
	else:
		log.error("Cannot convert image.")


@cli.command("send-images")
@click.option('-d', '--device', type=str, required=True, help="Device ID or device name.")
@click.option('-f', '--frame-rate', type=int, default=10, help="Send <INTEGER> frames per second. Default 10.")
@click.option('--normalize/--no-normalize', default=True, help="Normalize image to monochrome format. Default Enabled.")
@click.argument('bitmaps-folder', type=click.Path(exists=True))
@click.pass_obj
def send_images(it, device, frame_rate, normalize, bitmaps_folder):
	"""
	Send content of directory to specific device.

	List all files in given directory and send it to display with specific frame-rate.

	Recommended format is monochrome .bmp with 1-bit color depth but also other format such as .png can be used if normalize option is enabled.
	Normalization process try to convert image into standardized monochrome format but quality of results is questionable.
	"""
	if not os.path.isdir(bitmaps_folder):
		log.error("Given path '{}' is not a dictionary.".format(bitmaps_folder))
		return

	device_id = translate_device_name(it, device)
	if not device_id:
		return

	if frame_rate > 40:
		log.error("Wowow calm down! {} FPS? Are you kidding? This is not for gaming monitor. Maximum is 40 FPS.".format(frame_rate))
		return

	converted_images = []

	for file in [os.path.join(bitmaps_folder, f) for f in os.listdir(bitmaps_folder) if os.path.isfile(os.path.join(bitmaps_folder, f))]:
		img_bytes = it.convert_image_to_bytes(file, normalize)
		if img_bytes:
			converted_images.append(it.convert_bitmap_to_xbm_raw(img_bytes))

	log.info("Start images transmitting.")
	while True:
		for img in converted_images:
			it.mqtt.publish(it.get_display_topic(device_id), img, qos=0)
			time.sleep(1 / frame_rate)
		log.debug("Repeating display loop.")


@cli.command("pipe-interface")
@click.option('--buffer', type=int, default=4096, help="Size of input buffer in bytes. Default 4096.")
@click.option('-d', '--device', type=str, required=True, help="Device ID or device name.")
@click.option('--normalize/--no-normalize', default=True, help="Normalize image to monochrome format. Default Enabled.")
@click.argument('pipe_path', metavar="<PATH>", type=click.Path(exists=False))
@click.pass_obj
def pipe_interface(it, buffer, device, normalize, pipe_path):
	"""
	Create pipe interface for sending images.

	CAUTION: This function is supported only from linux systems or in Linux subsystem on Windows. If you use Linux subsystem on Windows pipe path must be in Linux filesystem.

	Command create named pipe in given <PATH> and listen in forever loop for incoming data. Data incoming into pipe are immediately send to given device.

	If image content is bigger than given buffer data will be incomplete and image sending failed.

	Recommended format is monochrome .bmp with 1-bit color depth but also other format such as .png can be used if normalize option is enabled.
	Normalization process try to convert image into standardized monochrome format but quality of results is questionable.

	EXAMPLE:

	\b
	In terminal 1 run:
	py ImageTransmitter.py -b broker.eu pipe-interface -d 950316592 ~/mypipe

	\b
	Int terminal 2 send data:
	cat image.bmp > ~/mypipe
	"""
	if os.name == 'nt':
		log.error("This command is not supported on OS Windows.")
		return

	device_id = translate_device_name(it, device)
	if not device_id:
		return

	try:
		if not os.path.exists(pipe_path):
			os.mkfifo(pipe_path)
	except AttributeError as e:
		log.error("Cannot create named pipe.")
		return
	except PermissionError as e:
		log.error("Cannot create named pipe. Permission denied.")
		log.error(e)
		return

	pipe_fd = os.open(pipe_path, os.O_RDONLY | os.O_NONBLOCK)

	import select
	poller = select.poll()
	poller.register(pipe_fd, select.POLLIN)
	log.info("Listening on pipe interface '{}'".format(pipe_path))

	while True:
		events = poller.poll()
		for fd, flags in events:
			if flags & select.POLLIN:
				# handling incoming data
				log.debug("Incoming data in pipe.")
				bytes = os.read(fd, buffer)

				img_file = io.BytesIO(bytes)  # create in-memory binary file
				img_bytes = it.convert_image_to_bytes(img_file, normalize)
				if img_bytes:
					xmb_bytes = it.convert_bitmap_to_xbm_raw(img_bytes)
					it.mqtt.publish(it.get_display_topic(device_id), xmb_bytes, qos=0)

			elif flags & select.POLLHUP:
				# handle when other side close pipe for writing
				poller.unregister(fd)
				# this open must be blocking otherwise it fall into forever loop
				fd_in = os.open(pipe_path, os.O_RDONLY)
				poller.register(fd_in, select.POLLIN)


@cli.command("get-devices")
@click.pass_obj
def get_devices(it):
	"""
	Obtain list of display devices.

	CAUTION: For this command must be EspHubServer running and listening on same MQTT broker.

	This command list all devices with connected display and show their IDs.
	"""
	uid = it.register_request()
	it.mqtt.publish(ImageTransmitter.get_request_topic(uid), "get_display_devices", qos=1)

	response = it.wait_for_response(uid)
	if response and response.get('status') == 'ok':
		print("-" * 35)
		print("| {:15}| {:15}|".format("device name", "device id"))
		print("-" * 35)
		for device in response.get('payload', list()):
			print("| {:15}| {:15}|".format(device.get('name'), device.get('id')))
		print("-" * 35)

		return response
	elif response and response.get('status') == 'nodata':
		print("No device with display found.")
		return None


def translate_device_name(it, device_name, timeout=1):
	"""
	Translate device name to device ID.
	If translation failed return device_name.
	If there is more device with same name, prompt user with device IDs.
	:param it: ImageTransmitter instance
	:type it: ImageTransmitter
	:param device_name: Name of device. Case insensitive.
	:param timeout: Waiting timeout.
	:return: Device ID.
	"""
	uid = it.register_request()
	it.mqtt.publish(ImageTransmitter.get_request_topic(uid), "get_device_id device_name='{}'".format(device_name), qos=1)

	response = it.wait_for_response(uid, timeout=timeout)
	if response and response.get("status") == 'ok':
		ids = response.get('payload')
		if len(ids) == 1:
			return ids[0]
		else:
			log.info("Multiple devices with same name found. Choose your device ID.")
			print("Devices with name '{}':".format(device_name))
			print("-" * 40)
			for id in ids:
				print("| {:37}|".format(id))
			print("-" * 40)
			return None
	elif response and response.get("status") == 'nodata':
		log.error("No device with name '{}' found.".format(device_name))
		log.info("Trying to send data to device with ID '{}'.".format(device_name))
		return device_name
	else:
		log.info("No response from server. Trying to send data to device with ID '{}'.".format(device_name))
		return device_name


if __name__ == "__main__":
	cli()
	# it = ImageTransmitter("tanas.eu")
	# it.register_topic(it.BASE_RESPONSE_TOPIC + "+")
	# print(translate_device_name(it, "node mcu"))