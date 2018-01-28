class Task(object):
	def __init__(self, name, interval, event, repeating=True):
		self.name = name
		self.interval = interval
		self.event = event
		self.repeating = repeating
		self.next_run = None

	def __str__(self):
		return str(self.__dict__)
