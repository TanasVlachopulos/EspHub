import json

from DataAccess import DBA, DAO, DAC
from Config import Config
from Plots import DisplayPlot
from Tools.Log import Log
from Tools import DateConvert
from DataProcessing import TimeSeriesOps
from datetime import datetime, timedelta

conf = Config.get_config()
log = Log.get_logger()


def get_actual_device_values(device_id, io_type='all'):
	"""
	Get actual values of device (newest record from database) and prepare for device detail card
	:param device_id: device ID
	:param io_type: select in/out type of ability, default 'all' select both 'in' and 'out'
	:return: JSON object with actual values, description, unit, ...
	"""
	device_values = []
	with DAC.keep_weak_session() as db:
		device = DBA.get_device(db, device_id)

		if device:
			for ability in device.abilities:
				# get newest record from db
				records = DBA.get_record_from_device(db, device_id, value_type=ability.name, limit=1)

				# select type of ability
				if ability.io == io_type or io_type == 'all':
					# select first item from record list or create empty dictionary if record list is empty
					if len(records) > 0:
						record_dict = records[0].serialize()
					else:
						record_dict = {}

					record_dict['value_type'] = ability.user_name
					record_dict['unit'] = ability.unit
					record_dict['category'] = ability.category
					record_dict['io'] = ability.io
					record_dict['desc'] = ability.description
					record_dict['user_name'] = ability.user_name
					record_dict['name'] = ability.name
					record_dict['id'] = ability.id
					device_values.append(record_dict)

	return device_values


def get_records_for_charts(device_id, value_type, from_date, to_date, summarization=None):
	"""
	Get record from database for plot and charts
	:param device_id: device ID
	:param value_type: name of ability
	:param from_date: start of time interval
	:type from_date: datetime.datetime
	:param to_date: end of time interval
	:type to_date: datetime.datetime
	:return: JSON object of time labels and values
	"""
	# TODO implement time interval from date - to date

	with DAC.keep_session() as db:
		records = DBA.get_record_from_device_between(db, device_id, from_date, to_date, value_type, order='asc')

		response = {
			# convert datetime objects to string according to summarization type
			# 'labels': [DateConvert.format_datetime(record.time, template=time_template) for record in records],
			'labels': [record.time for record in records],
			'values': [float(record.value) for record in records],
		}

		if summarization and summarization.lower() != "now":
			response = TimeSeriesOps.resample_data_vectors(response, 'labels', summarization)

		time_template = summarization if summarization else 'now'
		response['labels'] = [DateConvert.format_datetime(label, time_template) for label in response['labels']]
		return response


def get_all_input_abilities():
	"""
	Prepare input abilities for display setting
	:return: JSON list of devices witch provide input abilities and input abilities
	"""
	output = []
	with DAC.keep_session() as db:
		for device in DBA.get_devices(db):
			output_device = device.serialize()

			abilities_list = []
			for ability in device.abilities:
				if ability.io == DAO.Ability.IN:
					abilities_list.append(ability.serialize())

			if len(abilities_list) > 0:
				output_device['abilities'] = abilities_list
				output.append(output_device)

	return output


def render_plot_64base_preview(device_id, ability):
	now = datetime.now()
	plot_data = get_records_for_charts(device_id, ability, now - timedelta(1), now)
	plot = DisplayPlot.DisplayPlot(plot_data['values'], x_label_rotation=90)

	return plot.render_to_base64(width=320, height=240)


def get_screen_list(device_id, ability_name):
	with DAC.keep_session() as db:
		screens = DBA.get_display(db, device_id, ability_name)

		response_lst = []

		for screen in screens:
			print(screen)
			# source_device = db.get_device(screen.params.get('source_device'))  # load device to determine user names of device and ability
			# source_device = DBA.get_device(db, screen.params.get('source_device'))
			src_dev = screen.params.get('source_device')
			ability = screen.params.get('source_ability')

			print(src_dev, ability)
			plot = render_plot_64base_preview(screen.params.get('source_device'), screen.params.get('source_ability'))
			# print(plot)

			response_lst.append({
				'params': {
					'source_device_name': src_dev,
					'source_ability_name': ability,
					'base64_plot': plot
				}
			})

			#
			# screen.params['source_device_name'] = source_device.name
			#
			# # extract ability user name from provided_function JSON
			# source_device_abilities = source_device.abilities
			# for ability in source_device_abilities:
			# 	if ability.get('name') == screen.params.get('source_ability'):
			# 		screen.params['source_ability_name'] = ability.get('user_name')
			#

			print(response_lst)
			return response_lst
