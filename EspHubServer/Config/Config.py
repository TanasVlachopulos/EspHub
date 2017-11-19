import os, configparser


class Config(object):
	config = None
	path = None
	CONFIG_NAME = 'conf.ini'

	def __init__(self, setting_dir=None):
		config_parser = configparser.ConfigParser()

		if setting_dir:
			if not os.path.exists(setting_dir):
				os.makedirs(setting_dir)
			self.path = os.path.join(setting_dir, Config.CONFIG_NAME)
		else:
			self.path = self.CONFIG_NAME

		if not os.path.isfile(self.path):
			open(self.path, 'w').close()
		config_parser.read(self.path)

		Config.config = config_parser

	@staticmethod
	def get_config():
		if not Config.config:
			raise ValueError("Config is not initialized.")
		else:
			return Config.config

	@staticmethod
	def write_config(config):
		if not Config.path:
			raise ValueError("Config path is not initialized.")
		with open(Config.path, 'w') as file:
			config.write(file)
