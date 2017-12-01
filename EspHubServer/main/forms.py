from django import forms
from django.core import validators
from Config import Config

conf = Config.get_config()
input_abilities = conf.get('db', 'input_abilities').split(',')
output_abilities = conf.get('db', 'output_abilities').split(',')

class EditAbilityForm(forms.Form):
	id = forms.DecimalField(required=False)
	# name = forms.CharField(max_length=256, disabled=False, required=False)
	user_name = forms.CharField(label='Ability name', max_length=256, required=False)
	unit = forms.CharField(label='Value unit', max_length=16, required=False)
	description = forms.CharField(label='Description', max_length=500, required=False)

	input_choices = [(choice, choice.capitalize()) for choice in input_abilities]
	output_choices = [(choice, choice.capitalize()) for choice in output_abilities]
	choices = (
		('Input', input_choices),
		('Output', output_choices),
	)
	category = forms.ChoiceField(choices=choices, required=False)


class EditDeviceForm(forms.Form):
	validator_max_len = validators.MaxLengthValidator(64)
	name = forms.CharField(label='Device name', max_length=64, required=True, validators=[validator_max_len])
