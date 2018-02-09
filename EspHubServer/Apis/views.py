from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse
from django.forms import formset_factory
from main import forms
from Config.Config import Config
from Tools.Log import Log
from DataAccess import DAC, DBA
from datetime import datetime, timedelta
from main import data_parsing
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
