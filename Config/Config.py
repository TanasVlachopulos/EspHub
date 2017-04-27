import io
import configparser


class Config(object):
    CONFIG_PATH = 'conf.ini'

    def __init__(self):
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read(Config.CONFIG_PATH)

    def get_config(self):
        return self.config_parser

    def create_config(self):
        with open('test.ini', 'w') as conffile:
            conffile.write('test')
            conffile.flush()

    def __str__(self):
        return str(self.config_parser.sections())