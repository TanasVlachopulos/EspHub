# import datetime
# from Presentation.WebUi.DataAccess import DAO
import json
import time

from DeviceCom import DataCollector as collector
from DeviceCom import EspDiscovery as discovery
from Config import Config

conf = Config.Config().get_config()

collector.DataCollector(conf.get('db', 'path'), 'config')

msg = json.dumps({"name": conf.get('mqtt', 'server_name'),
                  "ip": conf.get('mqtt', 'ip'),
                  "port": conf.getint('mqtt', 'port')})

esp_discovery = discovery.EspDiscovery(conf.get('discovery', 'broadcast'),
                                       conf.getint('discovery', 'port'),
                                       msg,
                                       conf.getint('discovery', 'interval'))
esp_discovery.start()

# tel = DAO.Telemetry('123', datetime.datetime.now(), '0', '0', '0', '0', '0', '0')
# print(tel._time)
# print(tel.time)

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    exit(0)
