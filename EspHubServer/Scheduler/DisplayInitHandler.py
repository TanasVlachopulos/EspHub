from DisplayBusiness import DisplayScheduledTask
from Scheduler.ScheduledTask import ScheduledTask
from DataAccess import DAO, DBA, DAC


def init(args):
	"""
	Init Display scheduled event
	:param args: Dictionary with contains key 'id' = screen ID
	:return: List of ScheduledTask objects.
	"""
	screen_id = args.get('id')
	with DAC.keep_session() as db:
		screen = DBA.get_screen_by_id(db, screen_id)
		display = screen.display_ng

		# calculate rotation time (rotation of all screens for this display)
		time_sum = 0
		for s in display.screens:
			time_sum += s.rotation_period

		# calculate time offset (sum of time from previous displays)
		time_offset = 0
		index = display.screens.index(screen)
		for i in range(index):
			time_offset += display.screens[i].rotation_period

		task = ScheduledTask(task_type=DAO.Task.TYPE_DISPLAY,
							 interval=time_sum,
							 name=screen.name,
							 start_offset=time_offset,
							 event=DisplayScheduledTask.display_scheduled_task,
							 kwargs={'screen_id': screen_id}, )
		return [task]
