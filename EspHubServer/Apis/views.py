from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.forms import formset_factory
from main import forms
from Config.Config import Config
from Tools.Log import Log
from DataAccess import DAC, DBA

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

		print(edit_device_form.is_valid())
		print(edit_ability_formset.is_valid())

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
