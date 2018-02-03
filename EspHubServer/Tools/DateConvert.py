from datetime import datetime

templates = {'now': "%H:%M:%S",
			 'minutes': "%d.%m %H:%M",
			 'hours': "%d.%m %H",
			 'days': "%d.%m.%Y %H",
			 'weeks:': "%d.%m.%Y"}

def format_datetime(date_time, template='minutes', format=''):
	"""
	Format datetime object to string with given template or specific format.
	:param date_time: Datetime object.
	:type date_time: datetime
	:param template: Name of format template.
	:param format: Format string.
	:return: Datetime in string format.
	"""
	if format:
		return date_time.strftime(format)
	else:
		return date_time.strftime(templates.get(template, "minutes"))