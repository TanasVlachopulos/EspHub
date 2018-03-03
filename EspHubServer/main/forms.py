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


class BrokerSettingsForm(forms.Form):
	title = 'Broker settings'
	ip = forms.CharField(label='Broker address', max_length=128, required=True)
	port = forms.DecimalField(label='Broker port', required=True, initial=1883)
	server_name = forms.CharField(label='EspHub server name', required=True, max_length=128)


class DiscoverySettingsForm(forms.Form):
	title = 'Discovery settings'
	broadcast = forms.GenericIPAddressField(label='Discovery broadcast address', required=True)
	discovery_port = forms.DecimalField(label='Discovery port', required=True)
	interval = forms.DecimalField(label='Discovery interval', required=True, initial=5)


class ScreenSettingsForm(forms.Form):
	id = forms.IntegerField(required=False)  # only for internal form purposes, user cant change this
	rotation_period = forms.IntegerField(widget=forms.NumberInput(attrs={'type': 'range'}), label="Rotation period", required=True, min_value=10, max_value=300)
	width = forms.IntegerField(label='Width', min_value=1, required=False)
	height = forms.IntegerField(label='Height', min_value=1, required=False)
	x_offset = forms.IntegerField(label='X offset', min_value=0, required=False)
	y_offset = forms.IntegerField(label='Y offset', min_value=0, required=False)

class ScreenContentForm(forms.Form):
	"""
	Change screen content from Edit content page.
	"""
	content = forms.CharField(widget=forms.Textarea(), required=False)

class ScreenActionForm(forms.Form):
	"""
	Make action on screen like: move up, move down, delete.
	"""
	screen_id = forms.IntegerField(required=True)
	action = forms.CharField(required=True)

class AddScreenForm(forms.Form):
	"""
	Add new screen.
	"""
	name = forms.CharField(required=True, max_length=64, label='Name')
	description = forms.CharField(widget=forms.Textarea(attrs={'class': 'materialize-textarea'}), required=False, max_length=512, label='Description')