import paho.mqtt.client as mqtt
import socket

class EspHubUniversalLib(object):
	def __init__(self):
		self._abilities = []

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
		pass

	def send_json(self, topic_part, json_str):
		"""
		Send data to the server in raw JSON format with given topic header
		:param topic_part: Last part of MQTT message topic - device identificator (esp_hub/device/<device_id>/) is predefined
		:param json_str: String in JSON format to send to the server.
		:return:
		"""
		pass

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
	print("start")

