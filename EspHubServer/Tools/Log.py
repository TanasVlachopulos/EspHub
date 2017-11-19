import os, logging

class Log(object):
	logger = None
	LOG_PATH = 'esp_hub_server.log'

	def __init__(self):
		"""
		Init logger to console and file in library home directory.
		Tools has should have only one instance, so call get_logger method instead of constructor.
		"""
		path = self.LOG_PATH
		log = logging.getLogger("EspHubServer")
		log.setLevel(logging.DEBUG)
		lh = logging.FileHandler(path)
		ch = logging.StreamHandler()
		ch.setLevel(logging.DEBUG)
		ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
		log.addHandler(ch)
		lh.setLevel(logging.DEBUG)
		lh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
		log.addHandler(lh)
		Log.logger = log

	@staticmethod
	def get_logger():
		if not Log.logger:
			Log()
			return Log.logger
		else:
			return Log.logger