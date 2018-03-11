from PIL import Image

def ops(image):
	"""
	Make operations on image for SSD1306 display.
	Resize image to correct dimension and make it gray.
	:param image: Screenshot image.
	:type image: Image
	:return: Image
	"""
	img = image.resize((128, 64), resample=Image.LANCZOS)

	if img.mode == "RGBA":
		# replace alpha channel with white color
		img_data = img.load()
		for y in range(img.size[1]):
			for x in range(img.size[0]):
				if img_data[x, y][3] < 255:
					img_data[x, y] = (255, 255, 255, 255)
	# img.thumbnail([img.width, img.height], Image.ANTIALIAS)

	img = img.convert('L')  # convert image to monochrome (white = 0xff, black = 0x00)
	img_data = img.load()
	for y in range(img.size[1]):
		for x in range(img.size[0]):
			img_data[x, y] &= 1  # convert to 1 bit length 0xff -> 0x01, 0x00 -> 0x00
			img_data[x, y] ^= 1  # negate image bits

	return img

def convert_bitmap_to_xbm_raw(bitmap_bytes, x=0, y=0, height=64, width=64):
	"""
	Convert monochrome bitmap with 1-bit color depth into 8px per byte monochrome format.
	:param bitmap_bytes: Bytes of bitmap in format '0x00 0x01 0x00 0x01 ...'
	:param x: Starting X position on display.
	:param y: Starting Y position on display.
	:param height: Height of image.
	:param width: Width of image.
	:return: Bytearray with 8 pixels per byte.
	"""
	xbm_lst = []
	try:
		for i in range(0, len(bitmap_bytes), 8):
			# print(i, end=' ')
			pixel_byte = 0
			for bit in range(7, -1, -1):
				pixel_byte <<= 1
				pixel_byte |= bitmap_bytes[i + bit]

			xbm_lst.append(pixel_byte)
	except IndexError:
		pass

	xbm_lst.append(x)
	xbm_lst.append(y)
	xbm_lst.append(height)
	xbm_lst.append(width)

	return bytearray(xbm_lst)