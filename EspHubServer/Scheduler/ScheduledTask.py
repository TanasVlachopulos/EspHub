class ScheduledTask(object):
	def __init__(self, task_type, interval, event, kwargs=None, group_id=None, repeating=True):
		"""
		Init scheduled task.
		:param task_type: Type of task.
		:param interval: Scheduled interval in seconds.
		:param event: Event which will be fired.
		:param kwargs: Arguments for event.
		:param group_id: Specific group ID.
		:param repeating: Is repeating enabled.
		"""
		self.task_type = task_type
		self.interval = interval
		self.event = event
		self.kwargs = kwargs
		self.group_id = group_id
		self.repeating = repeating
		self.next_run = None

	def __str__(self):
		return str(self.__dict__)
