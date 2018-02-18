import time

from DisplayBusiness.WebWidgetServer import WebWidgetServer
from Tools.Log import Log
from threading import Thread, Event
from selenium import webdriver
import urllib.request
import socketserver
import random

log = Log.get_logger()


class WebScreenshot(object):
	DRIVER_CHROME = 'chrome'

	def __init__(self, width, height, screen_driver=DRIVER_CHROME, custom_driver_path=None, port=None, local_address=''):
		self.port = port if port else  random.randint(9000, 65000)
		self.local_address = local_address if local_address else 'localhost'

		if width < 64 or height < 32:
			log.error("Screenshot dimensions are too small.")
			return

		self.width =width
		self.height = height

		log.debug("Initiate Widget Web server.")
		self.end_event = Event()
		self.web_thread = Thread(target=WebScreenshot.render_web_widget, args=(self.end_event, self.port, local_address))
		self.web_thread.start()

		log.debug("Initiating Screenshot web browser.")
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		options.add_argument('window-size={}x{}'.format(width, height))

		self.driver = webdriver.Chrome(chrome_options=options)

	def take_screenshot(self, screen_id):
		"""

		:param screen_id:
		:return:
		"""
		log.debug("Taking screenshot of screen '{}' size {}x{}".format(screen_id, self.width, self.height))
		self.driver.get('http://{}:{}/{}'.format(self.local_address, self.port, screen_id))
		self.driver.save_screenshot('screen.png')

		# self.quit()


	def quit(self):
		"""
		Quit web browser instance and terminate web server.
		"""
		time.sleep(1)
		log.debug("Terminating Widget Web Server.")
		self.end_event.set()

		
		with urllib.request.urlopen('http://{}:{}/quit'.format(self.local_address, self.port), timeout=2) as r:
			r.read()

		self.web_thread.join()

		log.debug("Terminating screenshot web browser.")
		self.driver.quit()

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
