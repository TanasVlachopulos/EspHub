from DataAccess import DAO, DAC, DBA
from DeviceCom.MessageHandler import MessageHandler
from Tools.Log import Log
from Config import Config
import shlex
import json

log = Log.get_logger()
conf = Config.get_config()


class MqttApi(object):
	STATUS_OK = 'ok'
	STATUS_ERROR = 'error'
	STATUS_NO_DATA = 'nodata'

	def __init__(self, request, request_id=None):
		"""
		Initiate API request session.
		:param request: Request string in format: 'api_cmd arg1=val arg2="val with space" ...'
		:param request_id: User defined ID of request (UUID is recommended). ID is not mandatory, but when is undefined user cannot determinate request-response relationship.
		"""
		api_mapper = {'ping': self.ping,
					  'get_display_devices': self.get_display_devices,
					  'get_device_id': self.get_device_id, }

		tokenize_request = shlex.split(request)  # split request on spaces and preserved quoted substrings

		self.mqtt = MessageHandler(conf.get('mqtt', 'ip'), conf.getint('mqtt', 'port'))
		self.response_topic = "esp_hub/api/response/{}".format(request_id)

		api_request_cmd = tokenize_request[0]
		if api_request_cmd in api_mapper:
			api_callback = api_mapper[api_request_cmd]

			args = {}
			if len(tokenize_request) > 1:
				args = self.convert_args_list_to_dict(tokenize_request[1:])

			status, payload = api_callback(args)
			response = {'status': status, 'payload': payload, 'request_id': request_id}

			self.mqtt.publish(self.response_topic, json.dumps(response))

		else:
			log.error("Unknown MQTT API request '{}'.".format(api_request_cmd))

			response = {'status': self.STATUS_ERROR, 'request_id': request_id, 'payload': "Unknown request command {}".format(api_request_cmd)}
			self.mqtt.publish(self.response_topic, json.dumps(response))

	def convert_args_list_to_dict(self, args_list):
		"""
		Translate list of arguments into dictionary, like this: ['id=123', 'type=sensor'] -> {'id':'123', 'type':'sensor'}
		Ignore value data type, all values are String.
		:param args_list: List of arguments in format arg_name=arg_value
		:return: Arguments dictionary.
		"""
		args_dict = {}
		for arg in args_list:
			parts = arg.split('=')
			if len(parts) != 2:
				log.error("Invalid format of argument '{}' this argument cannot be processed.".format(arg))
			else:
				args_dict[parts[0]] = parts[1]

		return args_dict

	def ping(self, args):
		"""
		Callback for testing purposes. User can call ping for verification if server is running.
		:param args:
		:return: status, Simple test message.
		"""
		return self.STATUS_OK, "EspHubServer is now fully operational."

	def get_display_devices(self, args):
		"""
		Get all devices with connected display.
		:param args: Empty dict
		:return: status, payload - List of dictionaries contain information about devices and their displays in format: [{id, name, ability_name, ability_user_name, ability_description}, ...]
		"""
		with DAC.keep_session() as db:
			result = db.query(DAO.Device, DAO.Ability).join(DAO.Device.abilities).filter(DAO.Ability.category == DAO.Ability.CATEGORY_DISPLAY).all()

			if result:
				response = []
				for device, ability in result:
					response.append({'id': device.id,
									 'name': device.name,
									 'ability_name': ability.name,
									 'ability_user_name': ability.user_name,
									 'ability_description': ability.description, })
				return self.STATUS_OK, response
			else:
				return self.STATUS_NO_DATA, ""

	def get_device_id(self, args):
		"""
		Translate device name into device ID, if provided name is ID, return ID itself.
		Function is case insensitive. If there are more devices with same name return list of all matching IDs.
		:param args: Argument dictionary. Arguments: device_name (wanted device name)
		:return: status, payload - list of device IDs
		"""
		wanted_device_name = args.get('device_name')
		if not wanted_device_name:
			log.error("Missing argument 'device_name' in MQTT API request.")
			return self.STATUS_ERROR, "Missing argument 'device_name' in MQTT API request."

		with DAC.keep_session() as db:
			device = DBA.get_device(db, wanted_device_name)

			# if wanted_device_name is already existing device ID
			if device:
				return self.STATUS_OK, [device.id]

			results = DBA.get_devices_by_name(db, wanted_device_name)
			print(results)
			if results:
				return self.STATUS_OK, [device.id for device in results]
			else:
				return self.STATUS_NO_DATA, ""
