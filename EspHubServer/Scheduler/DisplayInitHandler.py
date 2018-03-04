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
		task = ScheduledTask(task_type=DAO.Task.TYPE_DISPLAY,
							 interval=screen.rotation_period,
							 event=DisplayScheduledTask.display_scheduled_task,
							 kwargs={'screen_id': screen_id}, )
		return [task]
