import os
import select

pipename = os.path.join(os.path.expanduser('~'), 'testroura')

class Descriptor(object):
	def __init__(self, fd):
		self.fd = fd

	def fileno(self):
		return self.fd

if __name__ == '__main__':
	try:
		if not os.path.exists(pipename):
			os.mkfifo(pipename)
	except AttributeError as e:
		print("cannot crate pipe")


	pipeout = open(pipename, 'r')
	# pipeout = os.open(pipename, os.O_WRONLY)

	pipein = os.open(pipename, os.O_RDONLY)
	pipein_obj = Descriptor(pipein)
	while True:
		readable, writ, exc = select.select([pipein_obj],[],[])
		if readable:
			print('some input', readable)
			# print(readable[0].readline())
			print(os.read(pipein, 25))
