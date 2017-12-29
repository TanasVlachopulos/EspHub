import configparser

import os

class Config(object):
	CONFIG_PATH = 'conf.ini'

	def __init__(self, setting_dir):
		self.config_parser = configparser.ConfigParser()
		if not os.path.exists(setting_dir):
			os.makedirs(setting_dir)
		self.path = os.path.join(setting_dir, Config.CONFIG_PATH)
		if not os.path.isfile(self.path):
			open(self.path, 'w').close()
		self.config_parser.read(self.path)

	def get_config(self):
		return self.config_parser

	def write_config(self, config):
		with open(self.path, 'w') as file:
			config.write(file)

	def __str__(self):
		return str(self.config_parser.sections())
