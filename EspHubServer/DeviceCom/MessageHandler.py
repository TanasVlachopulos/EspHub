"""
Wrap mosquito MQTT client and provide basic for receiving and sending data to MQTT broker
handle client and topics registrations
"""
from threading import Event
from Config import Config
from Tools.Log import Log
import paho.mqtt.client as mqtt

conf = Config.get_config()
log = Log.get_logger()


class _MessageHandler(object):
	def __init__(self, broker_addres, broker_port=1883, keep_alive=30, client_id="", username="", password=""):
		self.broker_address = broker_addres
		self.broker_port = broker_port
		self.keep_alive = keep_alive
		self.client_id = client_id
		self.username = username
		self.password = password

		self.client = None
		self.is_connected = Event()
		self.registered_topics = {}

		try:
			self._connect(client_id, username, password)
		except ConnectionRefusedError:
			log.critical(conf.get('msg', 'mqtt_error'))

	def _connect(self, client_id, username, password):
		if client_id:
			self.client = mqtt.Client(client_id=client_id)
		else:
			self.client = mqtt.Client()

		self.client.on_connect = self._on_connect_callback
		self.client.on_disconnect = self._on_disconnect_callback

		try:
			self.client.connect(self.broker_address, self.broker_port, self.keep_alive)
		# self.is_connected = True  # test only

		except TimeoutError:
			log.critical('Connection timeout. Remote MQTT broker is currently unavailable. Check whether the broker is running.')
			exit(0)

		self.client.loop_start()

	def _on_connect_callback(self, client, userdata, flags, rc):
		if rc == 0:
			log.info("Succesfully connected to broker")
			self.is_connected.set()
			self.register_topics(self.registered_topics)
		else:
			log.error("Connection error {}".format(str(rc)))

	def _on_disconnect_callback(self, client, userdata, rc):
		if rc != 0:
			log.error("Unexpected disconnection")
			self.is_connected.clear()

	def register_topic(self, topic, callback, qos=1):
		"""
		Register single topic and save it for reconnection event.
		:param topic: Topic string.
		:param callback: Callback function.
		:param qos: Qos level, default is 1.
		:return:
		"""
		if self.client and self.is_connected.wait(10):
			self.registered_topics[topic] = (callback, qos)
			self.client.subscribe(topic, qos=qos)
			self.client.message_callback_add(topic, callback)
		else:
			log.warning("Cannot register topic '{}' client is not connected.".format(topic))

	def register_topics(self, topics):
		"""
		Register topic as dictionary of topics in format:
		{'topic': callback} or {'topic': (callback, qos_level)}
		:param topics: Dictionary in defined format.
		:return:
		"""
		for topic, callback in topics.items():
			try:
				# register topic in format {'topic': (callback, qos_level)}, callback is tuple
				self.register_topic(topic, callback[0], callback[1])
			except TypeError:
				# register topic in format {'topic': callback}, callback is function
				self.register_topic(topic, callback)

	def publish(self, topic, payload, qos=0, retain=False):
		"""
		Wrap MQTT publish
		:param topic: Message topic
		:param payload: Message content
		:param qos: Message QOS (default 0)
		:param retain: Is retain message (default false)
		:return: None
		"""
		self.client.publish(topic, payload, qos=qos, retain=retain)

	def get_client_instance(self):
		"""
		Provide raw client instance
		:return: instance of MQTT paho client
		"""
		return self.client


class Singleton(type):
	_instance = {}

	def __call__(cls, *args, **kwargs):
		if cls not in cls._instance:
			cls._instance[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instance[cls]


class MessageHandler(_MessageHandler, metaclass=Singleton):
	pass
