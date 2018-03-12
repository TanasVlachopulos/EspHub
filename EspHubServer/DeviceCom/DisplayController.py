"""
DRAFT
 Drawing images on ILI display over MQTT - UNIMPLEMENTED and UNTESTED
"""
import json
from time import sleep

from DeviceCom import EscposImage as esci


class DisplayController(object):
	def __init__(self, mqtt_client_connection, device_topic):
		self._mqtt_client = mqtt_client_connection
		self._device_topic = device_topic

	def _send_to_display(self, json, topic_extension, qos=1):
		self._mqtt_client.publish(str.format("{}/{}", self._device_topic, topic_extension), json, qos=qos, retain=False)
		# sleep(0.002)

	def draw_bitmap(self, image, line_dense=5, x=0, y=0):
		self._send_to_display(json.dumps({"dense": line_dense}), "lineDense")
		delay = 0.001

		byte_parts = self._split_to_rows(image)
		self._set_bitmap_dimension(image.height, image.width, x, y)
		self.set_rotation(0)

		# self._send_to_display(json.dumps({"part": 0}), "part")
		# for all lines in bitmap with step lines=5
		for i in range(0, len(byte_parts), line_dense):
			self._send_to_display(json.dumps({"part": i}), "part")
			byte = b''.join(byte_parts[i:i + line_dense])  # merge bitmap lines to one byte array
			self._send_to_display(byte, "data", qos=0)
			sleep(delay)

		print("Sending bitmap data...")

	@staticmethod
	def _split_to_rows(image):
		# split bitmap to rows represented as bytes array
		divider = esci.EscposImage(image)
		return [part for part in divider.to_column_format(line_height=1)]

	def _set_bitmap_dimension(self, height, width, x=0, y=0):
		j = json.dumps({"w": width, "h": height, "x": x, "y": y})
		self._send_to_display(j, "dimension")

	def _set_window(self, x, y):
		j = json.dumps({"x": x, "y": y})
		self._send_to_display(j, "setWindow")

	def fill_screen(self, r, g, b):
		j = json.dumps({"r": r, "g": g, "b": b})
		self._send_to_display(j, "fillScreen")

	def draw_text(self, x, y, font_size, text):
		j = json.dumps({"x": x, "y": y, "textSize": font_size, "text": text})
		self._send_to_display(j, "drawText")

	def set_color(self, r, g, b):
		j = json.dumps({"r": r, "g": g, "b": b})
		self._send_to_display(j, "setColor")

	def set_font(self, name):
		j = json.dumps({"font": name})
		self._send_to_display(j, "setFont")

	def set_rotation(self, rotation):
		if 0 <= rotation <= 4:
			j = json.dumps({"rotation": rotation})
			self._send_to_display(j, "setRotation")
		else:
			print("Rotation must be in range 0 - 3")

	def draw_line(self, x1, y1, x2, y2):
		j = json.dumps({"x1": x1, "y1": y1, "x2": x2, "y2": y2})
		self._send_to_display(j, "drawLine")

	def draw_rect(self, x, y, w, h):
		j = json.dumps(({"x": x, "y": y, "w": w, "h": h}))
		self._send_to_display(j, "drawRect")

	def draw_fill_rect(self, x, y, w, h):
		j = json.dumps(({"x": x, "y": y, "w": w, "h": h}))
		self._send_to_display(j, "drawFillRect")

	def draw_circle(self, x, y, r):
		j = json.dumps(({"x": x, "y": y, "r": r}))
		self._send_to_display(j, "drawCircle")

	def draw_fill_circle(self, x, y, r):
		j = json.dumps(({"x": x, "y": y, "r": r}))
		self._send_to_display(j, "drawFillCircle")

	def draw_round_rect(self, x, y, w, h, r):
		j = json.dumps(({"x": x, "y": y, "w": w, "h": h, "r": r}))
		self._send_to_display(j, "drawRoundRect")

	def draw_fill_round_rect(self, x, y, w, h, r):
		j = json.dumps(({"x": x, "y": y, "w": w, "h": h, "r": r}))
		self._send_to_display(j, "drawFillRoundRect")

	def draw_button(self, x, y, text):
		self.draw_round_rect(x, y, x + 10 * len(text), 30, 5)
		self.set_color(255, 255, 255)
		self.draw_text(x + 10, y + 5, 2, text)
