import os, configparser


class Config(object):
	config = None
	path = None
	CONFIG_NAME = 'conf.ini'

	def __init__(self, setting_dir=None):
		"""
		Initialize config. Do this only once in module __init__.py.
		:param setting_dir: Path to config directory. If not set project root is used.
		"""
		config_parser = configparser.ConfigParser()

		if setting_dir:
			if not os.path.exists(setting_dir):
				os.makedirs(setting_dir)
			Config.path = os.path.join(setting_dir, Config.CONFIG_NAME)
		else:
			Config.path = Config.CONFIG_NAME

		if not os.path.isfile(Config.path):
			open(Config.path, 'w').close()
		config_parser.read(Config.path)

		Config.config = config_parser

	@staticmethod
	def get_config():
		"""
		Get configparser instance.
		:return: Configparser instance.
		"""
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
