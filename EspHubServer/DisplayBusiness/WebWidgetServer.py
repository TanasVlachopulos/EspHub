from http.server import BaseHTTPRequestHandler
from DataAccess import DAC, DBA
from Tools.Log import Log

log = Log.get_logger()


class WebWidgetServer(BaseHTTPRequestHandler):
	def do_GET(self):
		"""
		Override BaseHTTPRequestHandler do_GET.
		Handle urls '/screen_id' and obtain screen content from screen with given screen_id.
		Obtained content is send as HTTP response.
		If screen_id does not exist or URL is in bad format HTTP 404 error is returned.
		:return:
		"""
		# parse url string
		args_lst = self.path.split('/')
		if not len(args_lst) == 2 or not args_lst[1]:
			log.error("Internal error. Bad arguments count in WebWidget server.")
			self.send_response(404)
			return

		screen_id = args_lst[1]
		content = None

		# handle remote request for quit server
		if screen_id == 'quit':
			self.send_response(200)
			self.send_header('Content-type', 'text/html')
			self.end_headers()
			return

		# obtain screen from DB
		try:
			int_screen_id = int(screen_id)
			with DAC.keep_session() as db:
				screen = DBA.get_screen_by_id(db, int_screen_id)
				if not screen:
					log.warning("Requested screen '{}' does not exists in DB.".format(screen_id))
					self.send_response(404)
					return
				else:
					content = screen.content
		except ValueError:
			log.warning("Requested screen_id '{}' is not a number, request cannot be processed.".format(screen_id))
			self.send_response(404)
			return

		# check if screen has content
		if not content:
			log.warning("Requested screen '{}' has no content.".format(screen_id))
			self.send_response(404)
			return

		# render content as HTTP response
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

		self.wfile.write(content)
