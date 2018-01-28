from datetime import datetime, timedelta


class TaskScheduler(object):
	def __init__(self):
		self.tasks = []
		self._next_task = None

	def _find_next_task(self):
		"""
		Sort list with task and find nearest task.
		"""
		self.tasks = sorted(self.tasks, key=lambda task: task.next_run)
		self._next_task = self.tasks[0]

	def add_task(self, task):
		"""
		Add new task to task list and count next run time.
		:param task: Task object.
		"""
		task.next_run = datetime.now() + timedelta(0, task.interval)
		self.tasks.append(task)

	def get_time_to_next_task(self):
		"""
		Get time remaining to next task in seconds.
		:return: Time in seconds.
		"""
		self._find_next_task()
		sleep_time = self._next_task.next_run - datetime.now()
		return sleep_time.seconds if sleep_time.days >= 0 else 0

	def get_task(self):
		"""
		Get nearest task.
		:return: Task object.
		"""
		self._find_next_task()

		if self._next_task.next_run > datetime.now():
			return None

		if self._next_task.repeating:
			self._next_task.next_run = datetime.now() + timedelta(0, self._next_task.interval)
		else:
			self.tasks.remove(self._next_task)

		return self._next_task

