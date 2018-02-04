from datetime import datetime

templates = {'now': "%H:%M:%S",
			 'minutely': "%d.%m %H:%M",
			 'hourly': "%d.%m %H",
			 'daily': "%d.%m.%Y %H",
			 'weekly:': "%d.%m.%Y",
			 'monthly': '%m %Y'}

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