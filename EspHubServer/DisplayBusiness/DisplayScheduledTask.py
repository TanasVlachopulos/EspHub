from PIL import Image
from Tools.Log import Log
from DisplayBusiness.WebScreenshot import WebScreenshot
from DisplayBusiness import DisplaySsd1306Ops
from DataAccess import DAC, DBA, DAO
from DeviceCom.MessageHandler import MessageHandler
import io


log = Log.get_logger()

# dictionary of image operations function
# each display model has different parameters, this functions modify image object for specific display resolution, color ability, etc.
# functions accept PIL.Image instance and return PIL.Image instance
image_ops_handler = {
	DAO.DisplayNg.MODEL_SSD1306: DisplaySsd1306Ops.ops,  # operations for SSD1306 display
}

def display_scheduled_task(queue, screen_id):
	"""
	Run display scheduled task for screen with given ID.
	:param queue: Internal queue for MQTT messages. Messages putted into this queue will be send over mqtt.
	:param screen_id: ID of selected Screen.
	:return:
	"""
	log.debug("running task for screen with id: {}".format(screen_id))
	# time.sleep(60)

	ws = WebScreenshot()
	imb_bytes_file =  io.BytesIO(ws.take_screenshot(screen_id, ""))
	ws.quit()

	with DAC.keep_weak_session() as db:
		screen = DBA.get_screen_by_id(db, screen_id)
		display = screen.display_ng
		device_id = display.ability.device_id

	img = Image.open(imb_bytes_file)
	img = img.crop(box=(screen.x_offset, screen.y_offset, screen.x_offset + screen.height, screen.y_offset + screen.width))

	img_handler = image_ops_handler.get(display.model)
	if img_handler:
		img = img_handler(img)

	img_bytes = img.tobytes()
	xmb_bytes = DisplaySsd1306Ops.convert_bitmap_to_xbm_raw(img_bytes, height=img.height, width=img.width)

	response = {'topic': "esp_hub/device/{}/display".format(device_id),
				'message': xmb_bytes,
				'qos': 0}
	queue.put(response)





