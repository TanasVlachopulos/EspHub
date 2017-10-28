import configparser
import os
import paho.mqtt.client as mqtt
import socket
import json
import logging
import uuid


def _get_logger(path):
	log = logging.getLogger("EspHubUnilib")
	log.setLevel(logging.DEBUG)
	lh = logging.FileHandler(path)
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
	log.addHandler(ch)
	lh.setLevel(logging.DEBUG)
	lh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
	log.addHandler(lh)
	return log


class Config(object):
	CONFIG_PATH = 'conf.ini'

	def __init__(self, setting_dir):
		self.config_parser = configparser.ConfigParser()
		if not os.path.exists(setting_dir):
			os.makedirs(setting_dir)
		path = os.path.join(setting_dir, Config.CONFIG_PATH)
		if not os.path.isfile(path):
			open(path, 'w').close()
		self.config_parser.read(path)

	def get_config(self):
		return self.config_parser

	def __str__(self):
		return str(self.config_parser.sections())


class MqttHandler(object):
	def __init__(self, broker_addres, broker_port=1883, keep_alive=30, client_id="", username="", password=""):
		"""
		Handle connection to MQTT broker
		:param broker_addres:
		:param broker_port:
		:param keep_alive:
		:param client_id:
		:param username:
		:param password:
		"""
		self.broker_address = broker_addres
		self.broker_port = broker_port
		self.keep_alive = keep_alive
		self.client = None
		self.client_id = client_id
		self.is_connected = False
		self.log = _get_logger(os.path.join(os.path.expanduser('~'), EspHubUnilib._SETTING_DIR, 'esp_hub_unilib.log'))

		try:
			self._connect(client_id, username, password)
		except ConnectionRefusedError:
			self.log.error("Cannot connetct to MQTT broker")

	def _connect(self, client_id, username, password):
		self.client = mqtt.Client(client_id=client_id)
		self.client.on_connect = self._on_connect_callback
		self.client.on_disconnect = self._on_disconnect_callback

		try:
			self.client.connect(self.broker_address, self.broker_port, self.keep_alive)
			self.is_connected = True
		except TimeoutError:
			self.log.error(
				"Connection timeout. Remote MQTT broker is currently unavailable. Check whether the broker is running.")
			self.is_connected = False

		self.client.loop_start()

	def _on_connect_callback(self, client, userdata, flags, rc):
		if rc == 0:
			self.log.info("Successfully connected to MQTT broker")
			self.is_connected = True

	def _on_disconnect_callback(self, client, userdata, flags, rc):
		self.log.warning("Disconnected from MQTT broker")
		self.is_connected = False

	def register_topic(self, topic, callback, qos=1):
		"""
		Register specific topic for subscription
		:param topic: Subscribed topic
		:param callback: Callback function with signature (client, userdata, msg)
		:param qos: Qos level (default 1)
		:return:
		"""
		if self.client and self.is_connected:
			self.client.subscribe(topic, qos=qos)
			self.client.message_callback_add(topic, callback)

	def publish(self, topic, payload, qos=1, retain=False):
		"""
		Wrap MQTT publish
		:param topic: Message topic
		:param payload: Message content
		:param qos: Message QOS (default 0)
		:param retain: Is retain message (default false)
		:return: if client is connected True, if disconnected False
		"""
		if self.client and self.is_connected:
			res = self.client.publish(topic, payload, qos=qos, retain=retain)
			res.wait_for_publish()
			return True
		else:
			self.log.error("Cannot publish message, MQTT client is disconnected")
			return False


class EspHubUnilib(object):
	_MAIN_TOPIC = "esp_hub/device/"
	_DATA_TOPIC = "data"
	_TELEMETRY_TOPIC = "telemetry"
	_CMD_TOPIC = "cmd"
	_SETTING_DIR = '.esp_hub_unilib'

	def __init__(self, device_id=None):
		self._abilities = []
		self.log = _get_logger(os.path.join(os.path.expanduser('~'), EspHubUnilib._SETTING_DIR, 'esp_hub_unilib.log'))
		self.id = device_id if device_id else self._get_device_id()
		self.mqtt_client = None
		self.config = Config(os.path.join(os.path.expanduser('~'), EspHubUnilib._SETTING_DIR)).get_config()

	def _get_device_id(self):
		"""
		If device_id file exists load device id from file, otherwise create new UUID and create file
		:return: device UUID
		"""
		id_file = os.path.join(os.path.expanduser('~'), EspHubUnilib._SETTING_DIR)
		if not os.path.exists(id_file):
			os.makedirs(id_file)
		id_file = os.path.join(id_file, 'device_uuid')
		if os.path.isfile(id_file):
			with open(id_file, 'r') as file:
				uid = file.read()
				self.log.info("Device id loaded from file {}".format(uid))
				return uid.strip()
		else:
			uid = str(uuid.uuid4())
			self.log.info('New unique device id created: {}'.format(uid))
			with open(id_file, 'w') as file:
				file.write(uid)
			return uid

	@property
	def abilities(self):
		return self._abilities

	@abilities.setter
	def abilities(self, abilities):
		"""
		Set provided abilities which will be send to server.
		:param abilities: List of abilities name. Each name must be unique value. Abilities are case insensitive.
		:return:
		"""
		unique = []
		for ability in abilities:
			if not ability in unique:
				unique.append(ability)
		self._abilities = unique

	def send_data(self, ability, value):
		"""
		Send data to server for specific ability
		:param ability:
		:param value:
		:return:
		"""
		if ability in self._abilities:
			msg = {"type": ability,
				   "value": value,
				   "dvalue": 0}
			self.log.info("Sending data {}".format(ability))
			self.send_json(EspHubUnilib._DATA_TOPIC, json.dumps(msg))
		else:
			# TODO raise exception not registered ability
			pass

	def send_json(self, topic_part, json_str):
		"""
		Send data to the server in raw JSON format with given topic header
		:param topic_part: Last part of MQTT message topic.
			Standard topic format esp_hub/device/<device_id>/<topic_part> is predefined.
			Allowed topic part are: data/telemetry/cmd
		:param json_str: String in JSON format to send to the server.
		:return:
		"""
		if self.mqtt_client:
			topic = "{}{}{}".format(EspHubUnilib._MAIN_TOPIC, self.id, topic_part)
			self.mqtt_client.publish(topic, json_str)

	def server_discovery(self, timeout=60):
		"""
		Search for EspHubServer in local network
		:param timeout: Max time for response waiting in seconds.
		:return:
		"""
		pass

	def check_server(self, ip, port):
		pass

	def check_server_callback(self):
		pass

	def _generate_hello_msg(self):
		pass

	def send_telemetry_data(self):
		"""
		Send telemetry data from this device to the server.
		:return:
		"""
		local_ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
					 or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
						  [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]))[0]


if __name__ == "__main__":
	EspHubUnilib()
