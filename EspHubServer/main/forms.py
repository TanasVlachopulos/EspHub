from django import forms
from django.core import validators

class EditAbilityForm(forms.Form):
	id = forms.DecimalField()
	# name = forms.CharField(max_length=256, disabled=False, required=False)
	user_name = forms.CharField(label='Ability name', max_length=256, required=True)
	unit = forms.CharField(label='Value unit', max_length=16, required=False)
	description = forms.CharField(label='Description', max_length=500, required=False)
	# ablities= forms.ChoiceField(choices=[(1, 'second'), (2, 'asdf')])

class EditDeviceForm(forms.Form):
	validator_max_len = validators.MaxLengthValidator(64)
	device_name = forms.CharField(label='Device name', max_length=64, required=True, validators=[validator_max_len])



