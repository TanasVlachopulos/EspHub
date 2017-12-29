import logging

import os


class Log(object):
	logger = None

	def __init__(self):
		"""
		Init logger to console and file in library home directory.
		Log has should have only one instance, so call get_logger method instead of constructor.
		"""
		path = os.path.join(os.path.expanduser('~'), '.esp_hub_unilib')
		if not os.path.exists(path):
			os.makedirs(path)

		path = os.path.join(path, 'esp_hub_unilib.log')

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
		Log.logger = log

	@staticmethod
	def get_logger():
		if not Log.logger:
			Log()
			return Log.logger
		else:
			return Log.logger
