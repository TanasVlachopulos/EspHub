from DataAccess import DAO, DAC, DBA
from DeviceCom.MessageHandler import MessageHandler
from Tools.Log import Log
from Config import Config
import shlex
import json

log = Log.get_logger()
conf = Config.get_config()


class MqttApi(object):
	def __init__(self, request, request_id=None):
		"""
		Initiate API request session.
		:param request: Request string in format: "api_cmd
		:param request_id: User defined ID of request (UUID is recommended). ID is not mandatory, but when is undefined user cannot determinate request-response relationship.
		"""
		api_mapper = {'get_display_devices': self.get_display_devices, }

		tokenize_request = shlex.split(request)  # split request on spaces and preserved quoted substrings

		self.mqtt = MessageHandler(conf.get('mqtt', 'ip'), conf.getint('mqtt', 'port'))
		self.response_topic = "esp_hub/api/response/{}".format(request_id)

		api_request_cmd = tokenize_request[0]
		if api_request_cmd in api_mapper:
			api_callback = api_mapper[api_request_cmd]
			# TODO in future translate args list into args dictionary, like this: ['id=123', 'type=sensor'] -> {'id':'123', 'type':'sensor'}
			response = {'status': 'ok', 'request_id': request_id}
			if len(tokenize_request) > 1:
				response['payload'] = api_callback(tokenize_request[1:])
			else:
				response['payload'] = api_callback({})

			self.mqtt.publish(self.response_topic, json.dumps(response))

		else:
			log.error("Unknown MQTT API request {}.".format(api_request_cmd))

			response = {'status': "error", 'request_id': request_id, 'payload': "Unknown request command {}".format(api_request_cmd)}
			self.mqtt.publish(self.response_topic, json.dumps(response))

	def get_display_devices(self, args):
		"""
		Get all devices with connected display.
		:param args: Empty dict
		:return: List of dictionaries contain information about devices and their displays in format: [{id, name, ability_name, ability_user_name, ability_description}, ...]
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
				return response
