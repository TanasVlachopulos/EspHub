from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.forms import formset_factory
from main import forms
from Config.Config import Config
from Tools.Log import Log
from DataAccess import DAC, DBA, DAO
from datetime import datetime, timedelta
from main import data_parsing
from DisplayBusiness.WebScreenshot import WebScreenshot
import json

conf = Config.get_config()
log = Log.get_logger()


def edit_device_detail_post(request, device_id):
	"""
	Edit device detail such as name and abilities details
	:param request: Request.
	:param device_id: Device ID.
	:return: Redirect to device detail page.
	"""
	if request.method == 'POST':
		edit_device_form = forms.EditDeviceForm(request.POST)
		EditAbilityFormset = formset_factory(forms.EditAbilityForm)
		edit_ability_formset = EditAbilityFormset(request.POST)

		if edit_device_form.is_valid() and edit_ability_formset.is_valid():
			log.debug("Editing device '{}'.".format(device_id))

			with DAC.keep_session() as db:
				device = DBA.get_device(db, device_id)
				device.name = edit_device_form.cleaned_data.get('name')

				for form in edit_ability_formset:
					ability_id = form.cleaned_data.get('id')
					ability = DBA.get_ability_by_id(db, ability_id)
					ability.user_name = form.cleaned_data.get('user_name')
					ability.unit = form.cleaned_data.get('unit')
					ability.description = form.cleaned_data.get('description')
					ability.category = form.cleaned_data.get('category')

			return HttpResponseRedirect(reverse('main:device_detail', args=[device_id]))
		else:
			log.warning("form is invalid")
			return HttpResponse('fail')


def get_values(request, device_id, ability):
	"""
	Provide access to device records values.
	Return values as a JSON with list of values and list of time labels (data for rendering plots).
	:param request:
	:param device_id: ID of device.
	:param ability: Requested Ability name.
	:return:
	"""
	DATE_FORMAT = "%d.%m.%Y"

	try:
		if request.GET.get("to_date"):
			to_date = datetime.strptime(request.GET.get('to_date'), DATE_FORMAT)
		else:
			to_date = datetime.now()

		if request.GET.get("from_date"):
			from_date = datetime.strptime(request.GET.get('from_date'), DATE_FORMAT)
		else:
			from_date = to_date - timedelta(1)  # 1 day history

		if from_date > to_date:
			from_date, to_date = to_date, from_date  # swap dates
	except ValueError as e:
		log.error("Parsing date parameter fail: {}".format(e))
		return HttpResponseBadRequest("Parsing date parameter fail: {}".format(e))

	summarize = request.GET.get('summarize')
	response = data_parsing.get_records_for_charts(device_id, ability, from_date, to_date, summarization=summarize)
	return HttpResponse(json.dumps(response))


def get_screenshot(request, screen_id):
	"""

	:param request:
	:param screen_id:
	:return:
	"""
	ws = WebScreenshot(500, 500)
	screen = ws.take_screenshot_base64(screen_id)
	ws.quit()

	return HttpResponse(screen)


def edit_screens(request):
	"""
	POST method.
	Edit screen order or delete screen.
	:param request: Request.
	:return:
	"""
	log.debug("Screen action request.")
	if request.method == 'POST':
		screen_action_form = forms.ScreenActionForm(request.POST)

		if screen_action_form.is_valid():
			with DAC.keep_session() as db:
				screen = DBA.get_screen_by_id(db, screen_action_form.cleaned_data.get('screen_id'))
				display = screen.display_ng
				action = screen_action_form.cleaned_data.get('action')
				redirect_to = screen.id

				if action == 'up':
					index = display.screens.index(screen)
					if index != 0:
						previous_screen = display.screens[index - 1]
						previous_screen.order, screen.order = screen.order, previous_screen.order  # swap current order with previous screen
				elif action == 'down':
					index = display.screens.index(screen)
					if index != len(display.screens):
						next_screen = display.screens[index + 1]
						next_screen.order, screen.order = screen.order, next_screen.order  # swap current order with next screen order
				elif action == 'delete':
					if len(display.screens) <= 1:
						# handle when only 1 screen left in device - cannot be deleted
						log.warning('Cannot delete screen. At least one screen must be present.')
					else:
						log.info("Deleting display '{}' with ID: {}.".format(display.name, display.id))
						DBA.delete_screen_by_id(db, screen.id)  # delete screen
						redirect_to = [s.id for s in display.screens if s.id != screen.id][0]  # get first existing screen ID

				return HttpResponseRedirect(reverse('main:display_ng', kwargs={'ability_id': display.ability_id, 'screen_id': redirect_to}))

		else:
			log.error("Invalid ScreenAction Form.")
			return HttpResponseBadRequest("Invalid ScreenAction Form.")
	else:
		log.error("GET request is not allowed.")
		return HttpResponseBadRequest("GET request is not allowed.")


def add_screen(request, ability_id):
	"""
	POST method.
	Add new screen with name and description.
	:param request:
	:param ability_id: ID of base ability.
	:return:
	"""
	if request.method == 'POST':
		log.debug('Adding new screen')
		add_screen_form = forms.AddScreenForm(request.POST)

		if add_screen_form.is_valid():
			with DAC.keep_session() as db:
				display = DBA.get_display_ng(db, ability_id)
				if not display:
					log.warning("Ability with ID: {} does not exists.".format(ability_id))
					return HttpResponseBadRequest("Ability with ID: {} does not exists.".format(ability_id))
				max_order = max([s.order for s in display.screens])  # determinate maximum order number in display screens

				new_screen = DAO.Screen(name=add_screen_form.cleaned_data.get('name'),
										description=add_screen_form.cleaned_data.get('description'),
										order=max_order + 1,
										display_ng=display, )
				DBA.add_screen(db, new_screen)

				redirect_screen_id = [s.id for s in display.screens][0]  # select first screen of device for redirection (new once does not have ID yet)
				return HttpResponseRedirect(reverse('main:display_ng', kwargs={'ability_id': ability_id, 'screen_id': redirect_screen_id}))
		else:
			log.warning("Invalid value in form.")
			# TODO better handling
			return HttpResponseBadRequest("Invalid value in form.")


def edit_display(request, ability_id):
	"""
	POST method
	:param request:
	:param ability_id: ID of base ability.
	:return:
	"""
	if request.method == 'POST':
		log.debug("Edit display request.")
		display_setting_form = forms.DisplaySettingsForm(request.POST)

		if display_setting_form.is_valid():
			with DAC.keep_session() as db:
				display = DBA.get_display_ng(db, ability_id)
				if not display or not display.screens:
					log.warning("Ability with ID: {} does not exists.".format(ability_id))
					return HttpResponseBadRequest("Ability with ID: {} does not exists.".format(ability_id))

				display.model = display_setting_form.cleaned_data.get('model')
				# TODO save scheduler enable/disable

				return HttpResponseRedirect(reverse('main:display_ng', kwargs={'ability_id': ability_id, 'screen_id': display.screens[0].id}))