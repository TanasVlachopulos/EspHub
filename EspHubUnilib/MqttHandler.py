import paho.mqtt.client as mqtt
from Log import Log


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
		self.log = Log.get_logger()

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

	def _on_disconnect_callback(self, client, userdata, rc):
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
