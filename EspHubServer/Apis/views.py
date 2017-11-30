from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.forms import formset_factory
from main import forms
from Config.Config import Config
from Tools.Log import Log

conf = Config.get_config()
log = Log.get_logger()

def edit_device_detail_post(request):
	if request.method == 'POST':
		edit_device_form = forms.EditDeviceForm(request.POST)
		EditAbilityFormset = formset_factory(forms.EditAbilityForm)
		edit_ability_formset = EditAbilityFormset(request.POST)

		print(edit_device_form.is_valid())
		print(edit_ability_formset.is_valid())

		if edit_device_form.is_valid() and edit_ability_formset.is_valid():
			log.info('form is valid')
			print(edit_device_form.cleaned_data.get('device_id'))
			for form in edit_ability_formset:
				print(form.cleaned_data.get('user_name'))
		else:
			log.warning("form is invalid")

	return HttpResponse('fail')
