from django import forms
from  django.forms import formset_factory

class EditAbilityForm(forms.Form):
	user_name = forms.CharField(label='Ability name', max_length=256)
	unit = forms.CharField(label='Value unit', max_length=16)
	description = forms.CharField(label='Description', max_length=500)

class EditDeviceForm(forms.Form):
	device_name = forms.CharField(label='Device name', max_length=64)
	device_id = forms.HiddenInput()



