from DataAccess import DAO, DAC, DBA
from Scheduler import DisplayInitHandler
from Tools import Log
from datetime import datetime, timedelta
from multiprocessing import Event, Process, active_children
import time
import random

log = Log.Log.get_logger()

# Dictionary of initialization functions - key = task type, value = initialization function
# Initialization function must accept dictionary of arguments and return list of ScheduledTask objects
# example: init(args) -> Scheduler.ScheduledTask
task_init_handlers = {
	DAO.Task.TYPE_DISPLAY: DisplayInitHandler.init,  # handle display scheduler events initialization
}


class TaskScheduler(object):
	def __init__(self):
		self.tasks = []
		self._next_task = None

	def init_scheduled_tasks(self):
		"""
		Initialize tasks from database using type specific init functions.
		:return:
		"""
		with DAC.keep_session() as db:
			for task in DBA.get_active_tasks(db):
				task_init_handler = task_init_handlers.get(task.type)

				if task_init_handler:
					self.tasks += task_init_handler(task.params)
				else:
					log.error("Unknown task init function for task type '{}'.".format(task.type))

			for sch_task in self.tasks:
				# schedule first run with random jitter (0.3-3 s) which prevent overlapping of task starts
				sch_task.next_run = datetime.now() + timedelta(0, sch_task.interal) + (random.randint(300, 3000) / 1000)

	def _find_next_task(self):
		self.tasks = sorted(self.tasks, key=lambda task: task.next_run)
		self._next_task = self.tasks[0] if self.tasks else None

	def _get_time_to_next_task(self):
		sleep_time = self._next_task.next_run - datetime.now()
		sleep_time_seconds = sleep_time.seconds + (sleep_time.microseconds / 1000000)
		return sleep_time_seconds if sleep_time_seconds > 0 else 0

	def _get_task(self):
		"""
		Check if next_task is ready, if yes return it and schedule next repeating.
		:return: ScheduledTask object.
		:rtype: ScheduledTask
		"""
		if self._next_task.next_run > datetime.now():
			log.warning("Task is not ready yet. Internal error.")
			return None

		if self._next_task.repeating:
			self._next_task.next_run = datetime.now() + timedelta(0, self._next_task.interval)
		else:
			self.tasks.remove(self._next_task)

		return self._next_task

	def run_forever(self):
		"""
		Start task processing.
		Each task are spawned in separate process.
		:return: Event object. Processing task run until event is not set.
		:type:
		"""
		event = Event()
		while not event.is_set():
			## TODO handle some end event and do this in separate process
			self._find_next_task()
			sleep = self._get_time_to_next_task()
			time.sleep(sleep)
			task = self._get_task()

			process = Process(target=task.event, kwargs=task.kwargs,
							  name="{} (G:{})".format(task.task_type, task.group_id))
			process.start()

			running_processes = active_children()
			if len(running_processes) > 3:
				log.warning(
					"Too many running task processes: {} (count: {})".format([p.name for p in running_processes],
																			 len(running_processes)))
