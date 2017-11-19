import json

if __name__ == '__main__':
	from DataAccess import DBA, DAC, DAO

	with DAC.keep_session() as dbs:
		dev = DAO.Device(id='dev1234', name='My Test device', provided_func=['temp', 'hum'])
		dbs.add(dev)
		dbs.add(DAO.Record(name='temp', value='35', device=dev))
		dbs.add(DAO.Record(name='temp', value='36', device=dev))

		ability = DAO.Ability(device=dev)
		print(ability)
		json_str = {'name': 'ability1', 'user_name': 'Ability One', 'io': 'output'}
		ability.init_with_json(json.dumps(json_str))
		print(ability)
		dbs.add(ability)
		print(ability.to_json())


	# with DAC.keep_session() as dbs:
	# 	dev = dbs.query(DAO.Device).filter(DAO.Device.id == 'dev123').first()
	# 	print(dev.provided_func)
	# 	dev.provided_func = ['temp', 'hum', 'light']