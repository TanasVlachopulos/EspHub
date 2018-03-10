from Tools.Log import Log
import time

log = Log.get_logger()

def display_scheduled_task(screen_id):
	"""
	Rund display scheduled task for screen with given ID.
	:param screen_id:
	:return:
	"""
	log.info("running task for screen with id: {}".format(screen_id))
	time.sleep(60)