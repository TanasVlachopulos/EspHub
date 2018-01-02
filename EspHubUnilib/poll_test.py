import os
import select

pipename = os.path.join(os.path.expanduser('~'), 'testroura')

if __name__ == "__main__":
	try:
		if not os.path.exists(pipename):
			os.mkfifo(pipename)
	except AttributeError as e:
		print("cannot crate pipe")

	# open pipe for reading, NONBLOCK is not mandatory, but without nonblock open wait for first write to pipe
	pipein = os.open(pipename, os.O_RDONLY | os.O_NONBLOCK)

	poller = select.poll()
	poller.register(pipein, select.POLLIN)

	while True:
		events = poller.poll()
		print(events)
		for fd, flags in events:
			if flags & select.POLLIN:
				# handling incoming data
				print("input from:", str(fd))
				print(os.read(fd, 1024))
			elif flags & select.POLLHUP:
				# handle when other side close pipe for writing
				poller.unregister(fd)
				# this open must be blocking otherwise it fall into forever loop
				fd_in = os.open(pipename, os.O_RDONLY)
				poller.register(fd_in, select.POLLIN)