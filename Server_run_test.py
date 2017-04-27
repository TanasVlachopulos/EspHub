# import datetime
# from Presentation.WebUi.DataAccess import DAO
import json
import time

from DeviceCom import DataCollector as collector
from DeviceCom import EspDiscovery as discovery
from Config import Config
from DataAccess import DAO, DBA

conf = Config.Config().get_config()

# TODO osetrit chyby kt. tato trida vyzahuje pokud se nemuze pripojit na broadcast
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

# disp = DAO.Display(display_name='dislay', device_id='928532', screen_number=1, params="{}")
# disp2 = DAO.Display(display_name='dislay', device_id='928532', screen_number=2, params="{}")
# db = DBA.Dba(conf.get('db', 'path'))
# db.insert_display(disp)
# db.insert_display(disp2)

try:
    while True:
        time.sleep(0.2)
except KeyboardInterrupt:
    exit(0)
