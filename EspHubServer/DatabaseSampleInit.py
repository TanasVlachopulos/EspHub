import random

from DataAccess import DAC
from DataAccess.DAO import *
from datetime import datetime

if __name__ == "__main__":
	DAC._drop_db()
	with DAC.keep_session() as db:
		devices = []
		devices.append(Device(id='928528', name='Wemos D1', status=Device.VALIDATED))
		devices.append(Device(id='828529', name='testHello', status=Device.VALIDATED))
		devices.append(Device(id='828530', name='Output Test', status=Device.VALIDATED))
		devices.append(Device(id='828531', name='Node MCU', status=Device.VALIDATED))
		devices.append(Device(id='828535', name='Validation Test', status=Device.WAITING, provided_func=['temp', 'light']))

		for device in devices:
			db.add(device)

		abilities = []
		abilities.append(Ability(device=devices[0], name='light', user_name='Light', default_value='0', unit='Lux', io='in', description='', data_type='float'))
		abilities.append(Ability(device=devices[1], name='temperature', user_name='Temperature', io='in', category='sensor', default_value='0', data_type='float'))
		abilities.append(Ability(device=devices[1], name='display', user_name='Display', io='out', category='display'))
		abilities.append(Ability(device=devices[1], name='switch', user_name='Switch', io='out', category=Ability.CATEGORY_SWITCH, default_value='0'))
		abilities.append(Ability(device=devices[2], name='switch', user_name='Switch', io='out', category=Ability.CATEGORY_SWITCH, default_value='0'))
		abilities.append(Ability(device=devices[2], name='display', user_name='Display', io='out', category=Ability.CATEGORY_DISPLAY))
		abilities.append(Ability(device=devices[2], name='button', user_name='Butoooon', io='out', category=Ability.CATEGORY_BUTTON))
		abilities.append(Ability(device=devices[3], name='temp', user_name='Temperatur', io='in', category=Ability.CATEGORY_SENSOR))

		for ability in abilities:
			db.add(ability)

		db.add(Telemetry(device=devices[3], rssi='32', heap='11225', cycles='4584454441', voltage='3.3', ip='192.168.25.25', mac='11:22:33:44:55:66', ssid='tanet'))
		db.add(Telemetry(device=devices[0], rssi='32', heap='11225', cycles='4584454441', voltage='3.3', ip='192.168.25.25', mac='11:22:33:44:55:66', ssid='tanet'))

		for _ in range(100):
			db.add(Record(device=devices[0], time=datetime.now(), name='light', value=str(random.randint(100,300))))
			db.add(Record(device=devices[1], time=datetime.now(), name='temperature', value=str(random.randint(15,30))))
			db.add(Record(device=devices[3], time=datetime.now(), name='temp', value=str(random.randint(15,30))))
