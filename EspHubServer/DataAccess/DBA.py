from sqlalchemy import desc, and_, func
from DataAccess.DAO import *
from Tools.Log import Log
from datetime import datetime

log = Log.get_logger()


def add_waiting_device(session, device):
	"""
	add new device to waiting queue
	primary for Data collector which collect data from new devices
	:param session: Database session.
	:param device: DAO Device object.
	:type device: DAO.Device
	"""
	device.status = 'waiting'
	session.add(device)
	log.debug('Adding into waiting devices: {}.'.format(device))


def remove_waiting_device(session, device_id):
	"""
	Remove device from waiting list.
	:param session: Database session.
	:param device_id: ID of device
	:type device_id: str
	"""
	# TODO reimplement this. Stare chovani bylo takove ze se objekt odstranil z tabulky waiting devices a vytvoril se novy do tabulky devices, tady by bylo lepsi jenom zmenit status.
	raise NotImplementedError


def get_waiting_devices(session):
	"""
	Get all waiting devices.
	:param session: Database session.
	:return: List of DAO Device objects.
	"""
	return session.query(Device).filter(Device.status == Device.WAITING).all()


def get_devices(session):
	"""
	Get all devices which are not waiting.
	:param session: Database session.
	:return: List of DAO Device objects.
	"""
	return session.query(Device).filter(Device.status != Device.WAITING).all()


def get_device(session, device_id):
	"""
	Get single device with specific ID.
	:param session: Database session.
	:param device_id: Device ID.
	:type device_id: str
	:return: DAO Device object.
	"""
	return session.query(Device).get(device_id)

def get_devices_by_name(session, device_name):
	"""
	Get all devices with specific name. Searching ignore letter cases!
	:param session: Database session.
	:param device_name: Device name. Ignoring case insensitive.
	:return: List of DAO Device objects.
	"""
	return session.query(Device).filter(func.lower(Device.name) == func.lower(device_name)).all()

def insert_device(session, device):
	"""
	Insert device into database as validated device.
	:param session: Database session.
	:param device: DAO Device object.
	:type device: DAO.Device
	"""
	device.status = Device.VALIDATED
	session.add(device)
	log.debug("Add into devices: {}".format(device))


def remove_device(session, device_id, cascade=False):
	"""
	Remove Device with specific ID.
	:param session: Database session.
	:param device_id: ID of device
	:type device_id: str
	:param cascade: Enable or disable cascade deleting - default False, only Device will be deleted.
	:type cascade: bool
	:return Count of deleted devices.
	"""
	if cascade:
		deleted_abilities = session.query(Ability).filter(Ability.device_id == device_id).delete()
		deleted_displays = session.query(Display).filter(Display.device_id == device_id).delete()
		deleted_records = session.query(Record).filter(Record.device_id == device_id).delete()
		deleted_telemetry = session.query(Telemetry).filter(Telemetry.device_id == device_id).delete()
		deleted_devices = session.query(Device).filter(Device.id == device_id).delete()
		log.debug("{} devices, {} abilities, {} displays, {} records and {} telemetry was deleted.".format(deleted_devices, deleted_abilities, deleted_displays, deleted_records,
																										   deleted_telemetry))
		return deleted_devices
	else:
		deleted_devices = session.query(Device).filter(Device.id == device_id).delete()
		log.debug("{} devices was deleted.".format(deleted_devices))
		return deleted_devices


def update_provided_func(session, device_id, function):
	# This function was part of old DBA class, but is unnecessary
	raise NotImplementedError


def get_device_ability(session, device_id, ability_name):
	"""
	Get ability with specific name for given device.
	:param session: Database session.
	:param device_id: ID of device.
	:param ability_name: Name of ability.
	:return: Single DAO ability object.
	"""
	return session.query(Ability).filter(and_(Ability.name == ability_name, Ability.device_id == device_id)).first()


def get_ability_by_id(session, ability_id):
	"""
	Get ability with specific ID
	:param session: Database session.
	:param ability_id: ID of ability.
	:return: Single DAO Ability object.
	"""
	return session.query(Ability).get(ability_id)


def get_record_from_device(session, device_id, value_type=None, order='desc', limit=600):
	"""
	Get Records for given device_id.
	:param session: Database session.
	:param device_id: ID of parent Device.
	:type device_id: str
	:param value_type: Value 'name' from DAO Record.
	:type value_type: str
	:param order: Order of returned records ordered by parameter 'time'. Default is 'desc' any other value means ascending order.
	:param limit: Limit of returned records. Default is 600.
	:return: List of DAO Record objects.
	"""
	order_field = desc(Record.time) if order == 'desc' else Record.time
	if value_type:
		return session.query(Record).filter(and_(Record.device_id == device_id, Record.name == value_type)).order_by(order_field).limit(limit).all()
	else:
		return session.query(Record).filter(Record.device_id == device_id).order_by(order_field).limit(limit).all()

def get_record_from_device_between(session, device_id, from_date, to_date, value_type=None, order='desc'):
	"""
	Get Records for given device_id.
	:param session: Database session.
	:param device_id: ID of parent Device.
	:type device_id: str
	:param from_date: Record from this date.
	:type from_date: datetime
	:param to_date: Record to this date
	:type to_date: datetime
	:param value_type: Value 'name' from DAO Record.
	:type value_type: str
	:param order: Order of returned records ordered by parameter 'time'. Default is 'desc' any other value means ascending order.
	:return: List of DAO Record objects.
	"""
	order_field = desc(Record.time) if order == 'desc' else Record.time
	if value_type:
		return session.query(Record).filter(and_(Record.device_id == device_id, Record.name == value_type, Record.time.between(from_date, to_date))).order_by(order_field).all()
	else:
		return session.query(Record).filter(and_(Record.device_id == device_id, Record.device_id.between(from_date, to_date))).order_by(order_field).all()

def insert_record(session, record):
	"""
	Insert Record object into database.
	:param session: Database session.
	:param record: DAO Record object.
	:type record: DAO.Record
	"""
	session.add(record)
	log.debug("Add into records: {}".format(record))


def insert_telemetry(session, telemetry):
	"""
	Insert telemetry or update existing record if telemetry for given device exists. Each device has only one telemetry record stored in database
	because storing telemetry takes up space and is unnecessary to have telemetry history. Intentionally does not save a new object to the database
	but updates old because i dont want to do SQL select every time when telemetry arrive.
	This behaviour could be modified in modified in this function in future.
	:param session: Database session.
	:param telemetry: DAO Telemetry object.
	:type telemetry: DAO.Telemetry
	"""
	db_telemetry = session.query(Telemetry).filter(Telemetry.device_id == telemetry.device_id).first()
	if db_telemetry:
		db_telemetry.time = telemetry.time
		db_telemetry.rssi = telemetry.rssi
		db_telemetry.heap = telemetry.heap
		db_telemetry.cycles = telemetry.cycles
		db_telemetry.voltage = telemetry.voltage
		db_telemetry.ip = telemetry.ip
		db_telemetry.mac = telemetry.mac
		db_telemetry.ssid = telemetry.ssid
		db_telemetry.hostname = telemetry.hostname
		session.expunge(telemetry)  # new telemetry record must be expunged from session otherwise they are inserted into db
		log.debug("Updating telemetry: {}".format(db_telemetry))
	else:
		session.add(telemetry)
		log.debug("Add into telemetry: <{}>.".format(telemetry))


def get_telemetry(session, device_id):
	"""
	Get latest telemetry from given device id.
	:param session: Database session.
	:param device_id: ID of device.
	:type device_id: str
	:return: DAO Telemetry object.
	"""
	return session.query(Telemetry).filter(Telemetry.device_id == device_id).order_by(desc(Telemetry.time)).first()


def insert_display(session, display):
	"""
	Insert display into DB or update it if already exists. You should always check if display with same pair 'display_name' and 'screen_name'
	does not already exists, if it exists you should update old record not create new once.
	:param session: Database session.
	:param display: DAO Display object.
	:type display: DAO.Display
	"""
	session.add(display)
	log.debug("Add into Display: <{}>".format(display))


def update_display(session, display):
	"""
	Update existing display.
	:param session: Database session.
	:param display: DAO Display object.
	:type display: DAO.Display
	"""
	insert_display(session, display)


def get_display(session, device_id, display_name):
	"""
	Get all displays with given name and for given device. Table Display can contain more rows with same display name,
	each display can have more screens.
	:param session: Database session.
	:param device_id: ID of display parent device.
	:type device_id: str
	:param display_name: Display name.
	:type display_name: str
	:return: List of DAO Display objects.
	"""
	return session.query(Display).filter(and_(Display.device_id == device_id, Display.display_name == display_name)).all()


def get_screen(session, id):
	"""
	Get single screen by ID.
	:param session: Database session.
	:param id: Screen ID (primary key from table Display, not optional parameter screen_name)
	:type id: int
	:return: DAO Display object.
	"""
	return session.query(Display).get(id)
