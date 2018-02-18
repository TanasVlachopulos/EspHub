from DisplayBusiness.WebWidgetServer import WebWidgetServer
from Tools.Log import Log
from threading import Thread, Event
import socketserver
import random

log = Log.get_logger()


class WebScreenshot(object):
	def __init__(self, port=None, local_address=''):
		if not port:
			self.port = random.randint(9000, 65000)
		else:
			self.port = port

		self.end_event = Event()
		self.web_thread = Thread(target=WebScreenshot.render_web_widget, args=(self.end_event, self.port, local_address))
		self.web_thread.start()

	def take_screenshot(self, screen_id):
		"""

		:param screen_id:
		:return:
		"""
		self.end_event.set()
		# TODO get screenshot
		self.web_thread.join()

	@staticmethod
	def render_web_widget(end_event, port, local_address=''):
		"""
		Run HTTP server and render web widget until end_event is set.
		:param local_address: Local IP address of server, by default empty (localhost).
		:param port: Port of web server.
		:param end_event: Threading event which indicate end of server provisioning.
		:type end_event: Event
		:return:
		"""
		with socketserver.TCPServer((local_address, port), WebWidgetServer) as httpd:
			log.info("Web Widgetd Server starting at address: '{}', port: '{}.'".format(local_address, port ))
			while not end_event.is_set():
				httpd.handle_request()
