import json
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse
from django.forms import formset_factory
# from .models import Device
from main import data_parsing
from DataAccess import DAC, DAO, DBA
from DeviceCom import DataSender
from Config import Config
from Tools.Log import Log
from Plots import DisplayPlot
from main import forms

from datetime import datetime, timedelta

# TODO handle 404 page not found error
# TODO maximalizovat predavani hodnot do templatu - snizit pocet leteraru v templatech

conf = Config.get_config()
log = Log.get_logger()
input_abilities = conf.get('db', 'input_abilities').split(',')
output_abilities = conf.get('db', 'output_abilities').split(',')


def index(request):
	"""
	Main page with list of all devices
	:param request:
	:return: Main page
	"""
	with DAC.keep_session() as db:
		devices = DBA.get_devices(db)

		devices_id_lst = [device.id for device in devices]

		response = {'msg': 'Devices',
					'devices': devices,
					'devices_json': json.dumps(devices_id_lst),
					'time_to_live': 30,
					}
		return render(request, "main/index.html", response)


def device_detail(request, device_id):
	"""
	Device detail page
	:param request:
	:param device_id: device ID
	:return: device detail page
	"""
	with DAC.keep_session() as db:
		device = DBA.get_device(db, device_id)
		records = DBA.get_record_from_device(db, device_id, limit=10)

		actual_in_values = data_parsing.get_actual_device_values(device_id, io_type='in')
		actual_out_values = data_parsing.get_actual_device_values(device_id, io_type='out')

		# prepare forms for editing device
		AbilityFormset = formset_factory(forms.EditAbilityForm, max_num=0)
		ability_preset = [item.serialize() for item in device.abilities]
		ability_formset = AbilityFormset(initial=ability_preset)

		name_form = forms.EditDeviceForm({'name': device.name, 'device_id': device.id})

		response = {'device': device,
					'values': records,
					'actual_values': actual_in_values,
					'actual_out_values': actual_out_values,
					'device_status_interval': 30000,  # status refresh interval in seconds
					'device_values_interval': 3000,  # values refresh interval in seconds
					'edit_device_form': name_form,
					'edit_ability_formset': ability_formset
					}
		return render(request, 'main/device_detail.html', response)


def waiting_devices(request):
	"""
	List of all waiting device
	:param request:
	:return: waiting device page
	"""
	with DAC.keep_session() as db:
		devices = DBA.get_waiting_devices(db)

		response = {'title': 'Waiting devices',
					'devices': devices,
					'input_abilities': input_abilities,
					'output_abilities': output_abilities,
					}
		return render(request, 'main/waiting_devices.html', response)


def display(request, ability_name, device_id):
	"""
	Display setting page - allow sendig data to connected displays
	:param request:
	:param ability_name: name od display ability
	:param device_id: device ID
	:return: display setting page
	"""
	# plot_data = get_records_for_charts('8394748', 'DS18B20', 0, 0)
	# print(plot_data)
	# plot = DisplayPlot.DisplayPlot(plot_data['values'], x_label_rotation=90)

	# print(data_parsing.get_all_input_abilities())

	response = {
		'screens': data_parsing.get_screen_list(device_id, ability_name),  # list of screen settings
		'devices': data_parsing.get_all_input_abilities(),  # list of all devices and their input abilities
		'options': ['plot', 'text'],
		'ability_name': ability_name,
		'device_id': device_id,
		# 'plot': plot.render_to_base64(width=320, height=240),
	}

	return render(request, 'main/display.html', response)


def display_ng(request, ability_id, screen_id):
	if request.method == 'GET':
		with DAC.keep_session() as db:
			display = DBA.get_display_ng(db, ability_id)
			active_screen = DBA.get_screen_by_id(db, screen_id)

			screen_setting_form = forms.ScreenSettingsForm(active_screen.serialize())

			response = {
				'display': display,
				'active_screen': active_screen,
				'screen_setting': screen_setting_form,
			}

			return render(request, 'main/display_ng.html', response)

	elif request.method == 'POST':
		with DAC.keep_session() as db:
			active_screen = DBA.get_screen_by_id(db, screen_id)
			screen_setting_form = forms.ScreenSettingsForm(request.POST)

			if screen_setting_form.is_valid():
				active_screen.width = screen_setting_form.cleaned_data.get('width')
				active_screen.height = screen_setting_form.cleaned_data.get('height')
				active_screen.x_offset = screen_setting_form.cleaned_data.get('x_offset')
				active_screen.y_offset = screen_setting_form.cleaned_data.get('y_offset')
				active_screen.rotation_period = screen_setting_form.cleaned_data.get('rotation_period')

				return HttpResponseRedirect(reverse('main:display_ng', kwargs={'ability_id': ability_id, 'screen_id': screen_id}))
			else:
				#TODO handle invalid form - return same page with response key 'error msg'
				pass

	else:
		return HttpResponseNotAllowed("Invalid HTTP request method.")



def settings(request):
	"""
	Render setting page. Obtain setting forms and bind it with Configuration.
	Handle Get and Post requests.
	:param request:
	:return:
	"""
	formset = [
		{
			'title': forms.BrokerSettingsForm.title,
			'section_name': 'mqtt',
			'form': forms.BrokerSettingsForm
		},
		{
			'title': forms.DiscoverySettingsForm.title,
			'section_name': 'discovery',
			'form': forms.DiscoverySettingsForm,
		},
	]

	if request.method == 'GET':
		# handle page rendering

		# initiate forms with config data from given section
		for item in formset:
			form = item.get('form')  # get form class
			item['form'] = form(dict(conf.items(item.get('section_name'))))  # create instance and pass items from config

		return render(request, 'main/settings/server_setting.html', {'forms': formset})

	elif request.method == 'POST':
		# handle incoming data

		for item in formset:
			# loop in all subforms
			form_class = item.get('form')
			form = form_class(request.POST)

			# check if subform is valid
			if form.is_valid():
				section = item.get('section_name')
				log.info("Setting form section '{}' is valid.".format(section))
				conf_dic = dict(conf.items(section))

				for key, value in form.cleaned_data.items():
					if key in conf_dic:
						conf.set(section, key, str(value))  # update global configuration
					else:
						log.error("Item '{}' is not in config.".format(key))

		# TODO reload server if button 'save and restart' was pressed
		reload = request.POST.get('reload')  # if reload pressed then 'True' else 'False'

		log.info("Write changes into config file.")
		Config.write_config(conf)  # save global configuration
		return HttpResponseRedirect(reverse('main:settings'))
	else:
		log.error("Invalid type of HTTP request.")
		return HttpResponse('error')


""" FORMS """


def verify_device(request, device_id):
	with DAC.keep_session() as db:
		device = DBA.get_device(db, device_id)

		# if hidden remove input is set to false -> save new device to db
		if request.POST['remove-device'] == 'false':
			# sending MQTT message to device
			sender = DataSender.DataSender()
			sender.verify_device(device_id)
			device.status = DAO.Device.VALIDATED
			device.name = request.POST.get('device-name', device.name)

			for ability in device.provided_func:
				io_type = DAO.Ability.IN if request.POST['category-' + ability] in input_abilities else DAO.Ability.OUT
				dao_ability = DAO.Ability(device=device,
										  name=ability,
										  user_name=request.POST.get('user-name-' + ability),
										  category=request.POST.get('category-' + ability),
										  unit=request.POST.get('unit-' + ability),
										  description=request.POST.get('desc-' + ability),
										  io=io_type, )
				db.add(dao_ability)

			return HttpResponseRedirect(reverse('main:waiting_devices'))


def remove_device(request, device_id):
	"""
	Remove device from database
	:param request:
	:param device_id: device ID
	:return: redirect to home page
	"""
	with DAC.keep_session() as db:
		if request.POST['remove-device'] == 'true':
			log.info("device {} will be removed.".format(device_id))
			DBA.remove_device(db, device_id, cascade=True)

		return HttpResponseRedirect(reverse('main:index'))


def output_action(request, device_id, ability):
	"""
	Provide output action to devices. Convert UI events (button click, switch switch, ...) to MQTT messages.
	:param request:
	:param device_id: device ID
	:param ability: name of output ability
	:return: simple 'ok' message
	"""
	if request.is_ajax() and request.POST['device'] == device_id:
		sender = DataSender.DataSender()
		sender.send_data_to_device(request.POST['device'], request.POST['ability'], request.POST['state'])
		# sender.verify_device(device_id)
		log.info('sending {} {} {}'.format(request.POST['device'], request.POST['ability'], request.POST['state']))

	return HttpResponse('ok')


def save_screen(request, device_id):
	"""
	Receive screen parameters from display setting. Insert or update existing screen from DB. Action for 'add screen' and 'save' btn.
	:param request:
	:param device_id: parent device ID
	:return:
	"""
	if request.is_ajax() and request.POST.get('destination-device') == device_id and request.POST.get(
			'destination-display-name'):

		screen_id = request.POST.get('destination-screen-id')
		screen_params = {'source_device': request.POST.get('data-source-device'),
						 'source_ability': request.POST.get('data-source-ability')}

		db = DBA.Dba(conf.get('db', 'path'))
		if screen_id:
			# update display setting (already have screen_id)
			old_display = db.get_screen(screen_id)
			old_display.params = json.dumps(screen_params)
			db.update_display(old_display)

		else:
			# insert new display settings (dont have screen_id)
			new_display = DAO.Display(device_id=request.POST.get('destination-device'),
									  display_name=request.POST.get('destination-display-name'),
									  params=json.dumps(screen_params))
			db.insert_display(new_display)

	return HttpResponse('ok')


""" APIs """


def waiting_devices_api(request):
	"""
	Provide data about waiting devices
	:param request:
	:return: JSON list of all waiting devices
	"""
	with DAC.keep_session() as db:
		devices = DBA.get_waiting_devices(db)

		response = json.dumps([device.serialize() for device in devices])
		return HttpResponse(response)


def telemetry_api(request, device_id):
	"""
	Provide actual telemetry data
	:param request:
	:param device_id: device ID
	:return: JSON last telemetry record from DB
	"""
	with DAC.keep_session() as db:
		telemetry = DBA.get_telemetry(db, device_id)

		if telemetry:
			response = telemetry.to_json()
			return HttpResponse(response)
		else:
			return HttpResponse('{}')


def device_actual_values_api(request, device_id):
	"""
	Provide actual device values
	:param request:
	:param device_id: device ID
	:return: JSON last values records from DB
	"""
	device_values = data_parsing.get_actual_device_values(device_id)

	return HttpResponse(json.dumps(device_values))


def records_api(request, device_id, ability):
	"""
	Provide data for JS chart library
	:param request:
	:param device_id: device ID
	:param ability: name of ability
	:return: JSON with chart parameters and plot data with values and time lables
	"""
	now = datetime.now()
	past = now - timedelta(1)
	response = data_parsing.get_records_for_charts(device_id, ability, past, now)

	# convert datetime object to isoformat string
	response['chart_type'] = 'line'
	response['data_type'] = ability
	response['data_label'] = ability
	response['border_color'] = "#1e88e5"
	response['is_filled'] = 'false'

	return HttpResponse(json.dumps(response))


def display_preview_api(request, device_id, ability):
	"""
	Render Base64 plot preview for display setting page
	:param request:
	:param device_id: device ID
	:param ability: ability name
	:return: base64 uri with plot preview
	"""
	return HttpResponse(data_parsing.render_plot_64base_preview(device_id, ability))
