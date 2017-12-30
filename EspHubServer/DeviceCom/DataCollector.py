"""
Handle incoming messages form ESP devices and sending data to Db layer
Refactored
"""
from DataAccess import DAO, DAC, DBA
from DeviceCom.MessageHandler import MessageHandler
from DeviceCom.MqttApi import MqttApi
from Config.Config import Config
from Tools.Log import Log
import json
from datetime import datetime

conf = Config.get_config()
log = Log.get_logger()


class DataCollector(object):
	def __init__(self):

		# registered topics
		self.topics = {"esp_hub/device/hello": self.new_device_callback,
					   "esp_hub/device/+/telemetry": self.telemetry_callback,
					   "esp_hub/device/+/data": self.data_callback,
					   "esp_hub/api/request/+": self.api_callback,
					   }

		self.mqtt = MessageHandler(conf.get('mqtt', 'ip'), conf.getint('mqtt', 'port'))
		self.mqtt.register_topics(self.topics)

	@staticmethod
	def extract_payload(msg):
		"""
		Extract data msg from MQTT client
		:param msg: MQTT message
		:return: payload from device in json format
		"""
		return json.loads(msg.payload.decode("utf-8"))

	@staticmethod
	def extract_device_id(msg):
		"""
		Extract device id from topic string
		:param msg: MQTT message
		:return: device id
		"""
		part = [i for i in msg.topic.split('/')]
		return part[part.index("device") + 1]

	@staticmethod
	def verify_json(json_string):
		"""
		Verify if given string is JSON serializable.
		:param json_string: String for verification.
		:return: True/False
		"""
		try:
			json.loads(json_string)
			return True
		except json.JSONDecodeError:
			return False

	@staticmethod
	def normalize_ability_message(message):
		"""
		Try to normalize abilities message from device if this message is in invalid (not JSON serializable) format.
		:param message: Ability message from device.
		:type message: str
		:return: Normalized message.
		"""
		message = message.replace(';', ',')
		message = message.replace("'", '"')
		return message

	def new_device_callback(self, client, userdata, msg):
		"""
		Handle Hello msg from devices.
		Topic: esp_hub/device/hello
		"""
		data = self.extract_payload(msg)
		log.info("Receiving hello message from device: '{}', with ID: '{}'".format(data.get('name'), data.get('id')))

		with DAC.keep_session() as db:
			device = DBA.get_device(db, data.get('id'))
			if device and device.status == DAO.Device.VALIDATED:
				# device is in database and is validated
				log.info("Device {} is already validated. Sending Hello message.".format(device.name))
				reply = {'ip': conf.get('mqtt', 'ip'),
						 'port': conf.get('mqtt', 'port')}

				# TODO replace this with class DataSender
				self.mqtt.publish("esp_hub/device/{}/accept".format(device.id), json.dumps(reply))

			elif device and device.status == DAO.Device.WAITING:
				# device is in database and waiting for validation
				log.info("Device {} is already in database and waiting for validation.".format(device.name))

			elif not device:
				# device is not in database
				log.info("Device {} is not in database. Creating new device notification for user. Adding device into waiting devices.".format(data.get('id')))

				# check if information about abilities are in JSON serializable format
				abilities = None
				ability_raw_data = data.get('ability')
				if isinstance(ability_raw_data, list):
					abilities = ability_raw_data
				elif self.verify_json(ability_raw_data):
					abilities = json.loads(ability_raw_data)
				else:
					log.warning("Abilities received from device '{}' are in invalid format.".format(data.get('name')))
					try:
						normalized_data = self.normalize_ability_message(ability_raw_data)
						abilities = json.loads(normalized_data)
					except (json.decoder.JSONDecodeError, ValueError):
						log.error("Cannot parse abilities provided by device '{}'.".format(data.get('name')))

				# add device to waiting list
				if abilities:
					new_device = DAO.Device(id=data.get('id'), name=data.get('name'), provided_func=abilities)
					DBA.add_waiting_device(db, new_device)

	def telemetry_callback(self, client, userdata, msg):
		"""
		Handle telemetry messages from devices
		Topic: esp_hub/device/+/telemetry
		"""
		data = self.extract_payload(msg)
		device_id = self.extract_device_id(msg)

		log.info("Receiving telemetry message from device with ID: '{}'".format(device_id))

		with DAC.keep_session() as db:
			device = DBA.get_device(db, device_id)
			if device and device.status == DAO.Device.VALIDATED:
				telemetry = DAO.Telemetry(device=device,
										  time=datetime.now(),
										  device_id=device.id,
										  rssi=data.get('rssi'),
										  heap=data.get('heap'),
										  cycles=data.get('cycles'),
										  ip=data.get('local_ip'),
										  mac=data.get('mac'),
										  voltage=data.get('voltage'),
										  ssid=data.get('ssid'),
										  hostname=data.get('hostname'))
				DBA.insert_telemetry(db, telemetry)
			else:
				log.warning("Device with ID '{}' is not in database of validated devices. Cannot store telemetry.".format(device_id))

	def data_callback(self, client, userdata, msg):
		"""
		Handle messages from device witch contain measured data
		Topic: esp_hub/device/+/data
		"""
		data = self.extract_payload(msg)
		device_id = self.extract_device_id(msg)

		# check if message contain mandatory fields
		if 'type' in data and 'value' in data:
			log.info("Data from '{}' >>> type: {}, value: {}".format(device_id, data.get('type'), data.get('value')))

			with DAC.keep_session() as db:
				device = DBA.get_device(db, device_id)
				# check if device is in database
				if device and device.status == device.VALIDATED:
					record = DAO.Record(device=device,
										time=datetime.now(),  # this line is important, default time is time of module DAO initialization
										name=data.get('type'),
										value=data.get('value'))
					DBA.insert_record(db, record)
				else:
					log.warning("Device with ID '{}' is not in database of validated devices. Cannot store record.".format(device_id))
		else:
			log.error("Message from device with ID '{}' is in incomplete format.".format(device_id))

	def api_callback(self, client, userdata, msg):
		"""
		Handle API request over MQTT.
		Topic: "esp_hub/api/request/+"
		Commands: list_devices
		"""
		data = msg.payload.decode('utf-8')

		part = [i for i in msg.topic.split('/')]
		if len(part) > 3:
			request_id = part[part.index("request") + 1]
			MqttApi(data, request_id)
		else:
			MqttApi(data)
