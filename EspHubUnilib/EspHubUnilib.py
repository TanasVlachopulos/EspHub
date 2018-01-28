import configparser
import threading
import select
import os
import socket
import json
import uuid
import time

from Log import Log
from Config import Config
from MqttHandler import MqttHandler
from Task import Task
from TaskScheduler import TaskScheduler


class EspHubUnilib(object):
	_MAIN_TOPIC = "esp_hub/device/"
	_HELLO_TOPIC = "hello"
	_DATA_TOPIC = "data"
	_TELEMETRY_TOPIC = "telemetry"
	_CMD_TOPIC = "cmd"
	_ACCEPT_TOPIC = 'accept'
	_SETTING_DIR = '.esp_hub_unilib'
	DISCOVERY_PORT = 11114

	def __init__(self, name="", device_id=None, config_path=None):
		self.log = Log.get_logger()
		self.config = Config(os.path.abspath(config_path)) if config_path else Config(os.path.abspath('.')).get_config()

		self.id = device_id if device_id else self._get_device_id()
		self.name = name

		self.tasks = self._parse_tasks()  # load abilities from config file
		self._abilities = [task.name for task in self.tasks]

		# indicate if hello message has been sent to server and client wait for hello response
		self.waiting_for_hello_response = threading.Event()
		self.server_candidate = None  # candidate for future server received from UDP discovery
		self.validated = False

	def start(self):
		broker_info = self._get_broker_config()
		# try to connect with config values
		if broker_info and self.check_server(broker_info.get('address'), broker_info.get('port')):
			self.log.info("Using config values for connection: server = {}, port = {}".format(broker_info.get('address'), broker_info.get('port')))
			validation_interval = self.config.getint('common', 'accept-timeout', fallback=20)

			# wait for server accept msg
			if self.waiting_for_hello_response.wait(timeout=validation_interval):
				self.log.info("Server {} has been validated. Connected with HubServer.".format(broker_info.get('address')))
				self.waiting_for_hello_response.clear()
			else:
				self.log.error("Server {} has not been validate in given time {} seconds.".format(broker_info.get('address'), validation_interval))
		else:
			self.server_discovery()

		task_scheduler = TaskScheduler()
		for task in self.tasks:
			task_scheduler.add_task(task)

		self.log.debug("Starting mainloop.")
		while self.validated:
			time.sleep(3) # todo sleep for time from task scheduler
			# todo get current task and call this function
			# todo return result over mqtt

	# TODO send telemetry

	def _parse_tasks(self):
		"""
		Load config file, parse all abilities sections and create list of Tasks
		:return: List of Task objects.
		"""
		tasks = []
		for section in self.config.sections():
			if not section == 'common':
				external_module = __import__(self.config.get(section, 'script_path'))
				event = getattr(external_module, self.config.get(section, 'function', fallback='run'))
				# todo handle variouse exception during loading module, module cannot have .py appendix

				task = Task(section,
							self.config.getint(section, 'interval'),
							event)
				tasks.append(task)

		return tasks

	def _get_broker_config(self):
		"""
		Obtain broker address and broker port from configuration file.
		:return: Dictionary contains key 'address' and 'port'
		"""
		try:
			return {'address': self.config.get('common', 'broker-address'),
					'port': self.config.getint('common', 'broker-port')}
		except configparser.NoSectionError:
			self.log.info("No broker section in config file found.")
			return None
		except configparser.NoOptionError:
			self.log.info("Config file missing some sections.")
			return None

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
			self.log.debug("Sending data {}".format(ability))
			self.send_json(EspHubUnilib._DATA_TOPIC, json.dumps(msg))
		else:
			self.log.error("Cannot send not registered ability.")
			raise ValueError("Cannot send not registered ability.")

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
			topic = "{}{}/{}".format(EspHubUnilib._MAIN_TOPIC, self.id, topic_part)
			if not self.mqtt_client.publish(topic, json_str):
				raise ConnectionError("Cannot publish message, MQTT client is disconnected.")

	def server_discovery(self, timeout=60):
		"""
		Search for EspHubServer in local network
		:param timeout: Max time for response waiting in seconds.
		:return:
		"""
		broadcast_ip = ''
		udp_port = EspHubUnilib.DISCOVERY_PORT

		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# sock.settimeout(timeout)
		sock.bind((broadcast_ip, udp_port))

		final_time = time.time() + timeout

		self.log.info("Start server discovery.")
		while not self.validated:
			try:
				left_time = final_time - time.time()
				if left_time > 0:
					sock.settimeout(left_time)
				else:
					self.log.error("Server discovery timeout.")
					break
				data, addr = sock.recvfrom(1024)
				incoming_data = json.loads(data.decode('utf-8'))
				self.log.debug("Receiving UDP message from {}.".format(addr))

				# try to use server from incoming message
				if self.check_server(incoming_data.get('ip'), incoming_data.get('port')):
					validation_interval = self.config.getint('common', 'accept-timeout', fallback=20)

					# wait for hello response
					if self.waiting_for_hello_response.wait(timeout=validation_interval):
						self.log.info("Server {} has been validated.".format(incoming_data.get('ip')))
						self.waiting_for_hello_response.clear()
						break
					else:
						self.log.error("Server {} has not been validate in given time {} seconds.".format(incoming_data.get('ip'), validation_interval))

			except socket.timeout:
				self.log.error("Server discovery timeout.")
				break
			except ValueError:
				self.log.warning("UDP discover message invalid format.")

	def check_server(self, ip, port):
		"""
		Check if server candidate from UDP discovery msg is valid MQTT server
		:param ip: Server ip or hostname.
		:param port: Server port.
		:return true/false
		"""
		client = MqttHandler(ip, port, client_id=self.id)
		if client.is_connected:
			self.log.debug("Successfully connected to server candidate.")
			client.register_topic("{}{}/{}".format(EspHubUnilib._MAIN_TOPIC, self.id, EspHubUnilib._ACCEPT_TOPIC),
								  self.check_server_callback)
			self.mqtt_client = client
			self.server_candidate = {'ip': ip, 'port': port}
			self._generate_hello_msg()
			return True
		else:
			self.log.error("Cannot connect to server candidate.")
			return False

	def check_server_callback(self, client, userdata, msg):
		"""
		Handler Accept message (response to Hello message) from server
		"""
		self.log.info("Receiving hello message.")
		try:
			server_reply = json.loads(msg.payload.decode("utf-8"))

			# handle if port number is string, caste string to int
			if isinstance(server_reply.get('port'), str) and server_reply.get('port').isdigit():
				server_reply['port'] = int(server_reply.get('port'))

			self.log.debug("Hello reply: {}".format(server_reply))

			# compare server candidate against hello message
			if self.server_candidate == server_reply:
				self.log.info("Hello response validated.")
				self._write_server_to_config(server_reply.get('ip'), server_reply.get('port'))
				self.validated = True
				self.waiting_for_hello_response.set()
			else:
				print(self.server_candidate)
				self.log.error("Server candidate does not match Hello reply.")

		except json.JSONDecodeError as e:
			self.log.error("Cannot parse hello reply. Error: {}".format(e))
		except ValueError as e:
			self.log.error("Invalid data type in hello reply. Error: {}".format(e))

	def _generate_hello_msg(self):
		"""
		Send hello message to server candidate
		"""
		msg = {'name': self.name,
			   'id': self.id,
			   'ability': self._abilities}
		self.log.info("Sending hello message to server candidate.")
		self.mqtt_client.publish("{}{}".format(EspHubUnilib._MAIN_TOPIC, EspHubUnilib._HELLO_TOPIC), json.dumps(msg))

	def send_telemetry_data(self):
		"""
		Send telemetry data from this device to the server.
		:return:
		"""
		local_ip = (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")]
					 or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in
						  [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]))[0]

	def _write_server_to_config(self, ip, port):
		config_handler = Config(os.path.join(os.path.expanduser('~'), EspHubUnilib._SETTING_DIR))
		config = config_handler.get_config()
		if not 'broker' in config:
			config.add_section('broker')
		config.set('broker', 'address', ip)
		config.set('broker', 'port', str(port))
		config_handler.write_config(config)


if __name__ == "__main__":
	lib = EspHubUnilib('test device')
	lib.start()
