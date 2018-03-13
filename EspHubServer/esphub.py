from django.core.management import call_command
from django.core.management.commands.runserver import BaseRunserverCommand
from Config import Config
from DeviceCom import DataCollector as Collector
from DeviceCom import EspDiscovery as Discovery
from Scheduler import TaskScheduler
# from .. import run_django
from Tools.Log import Log
import threading
import django
import os
import sys
import json
import time
import click
import signal
import uuid

# Variable for PeriodicDisplay task, is global due to signal_handling
task_to_stop = []
log = Log.get_logger()


class HackedRunserver(BaseRunserverCommand):
	def inner_run(self, *args, **options):
		print('before runserver')
		super(HackedRunserver, self).inner_run(*args, **options)
		print('after runserver')


def _exit_signal_handler(signal, frame):
	log.info("Keyboard interrupt!")
	for task in task_to_stop:
		task.stop()

	for task in task_to_stop:
		task.join(10)

	# raise keyboard interrupt again for stopping Django webserver
	raise KeyboardInterrupt


def _device_discovery(endless=True):
	"""
	Start device discovery function
	:param endless: run discovery in endless loop (default true)
	:return:
	"""
	conf = Config.get_config()

	key_file_path = conf.get("main", "server_key_file")
	server_key = ""
	if os.path.isfile(key_file_path):
		with open(key_file_path, 'r') as f:
			server_key = f.read()
			log.info("Server key loaded from file: '{}'".format(server_key))
	else:
		log.critical("Server key file not found.")
		return

	msg = json.dumps({"name": conf.get('mqtt', 'server_name'),
					  "ip": conf.get('mqtt', 'ip'),
					  "port": conf.getint('mqtt', 'port'),
					  "server_key": server_key})

	esp_discovery = Discovery.EspDiscovery(conf.get('discovery', 'broadcast'),
										   conf.getint('discovery', 'discovery_port'),
										   msg,
										   conf.getint('discovery', 'interval'), )
	esp_discovery.start()
	task_to_stop.append(esp_discovery)

	if endless:
		while True:
			time.sleep(0.5)


def _collect_data(endless=True):
	"""
	Start collecting data from devices
	:param endless: run collecting iin endless loop (default true)
	:return:
	"""
	Collector.DataCollector()

	if endless:
		try:
			while True:
				time.sleep(0.5)
		except KeyboardInterrupt:
			log.info("Process terminated")
			exit(0)


def _run_task_scheduler(endless=True):
	"""
	Start task scheduler which handle record from table Task.
	:param endless: Run scheduler in endless loop.
	:return: Task scheduler object if endless is False.
	"""
	scheduler = TaskScheduler.TaskScheduler()
	task_to_stop.append(scheduler)
	scheduler.start()

	if endless:
		try:
			while True:
				time.sleep(1)
				if not scheduler.is_alive():
					log.error("Task scheduler process is dead.")
		except KeyboardInterrupt:
			log.debug("Start terminating process.")
			scheduler.stop()
			scheduler.join(10)  # depend on join timeout in task scheduler
			log.info("Process terminated")
		finally:
			exit(0)
	else:
		return scheduler


@click.group()
def cli():
	"""EspHub home automation server"""

	conf = Config.get_config()

	# initiate server key if not exists
	key_file_path = conf.get("main", "server_key_file")
	if not os.path.isfile(key_file_path):
		server_key = str(uuid.uuid4())
		log.info("New server ID initiating: '{}'".format(server_key))
		dir_path, filename = os.path.split(key_file_path)
		os.makedirs(dir_path, exist_ok=True)
		with open(key_file_path, 'w') as f:
			f.write(server_key)
	else:
		log.info('Loading existing server ID.')

	# magic with system path
	sys.path.append('..')
	sys.path.append('/EspHubServer')
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EspHubServer.settings')


@cli.command()
@click.option('--discovery/--no-discovery', default=True, help='Device discovery function (default enable)')
@click.option('--collecting/--no-collecting', default=True, help='Collecting data from devices (default enable)')
@click.option('--web-app-only/--full-app', default=False,
			  help='Run only web interface without other functions (default disabled)')
@click.argument('address-port', default='', metavar='[ipaddr:port]')
def start(discovery, collecting, task_scheduler, web_app_only, address_port):
	"""
	Start EspHub server with all functions

	\b
	Arguments:
		ipaddr:port     Optional port number, or ipaddr:port
	"""
	# handle interrupt signal when user press ctrl+c
	signal.signal(signal.SIGINT, _exit_signal_handler)

	# start collecting data
	if collecting and not web_app_only:
		_collect_data(endless=False)
	else:
		log.info("collecting disabled")

	# start discovery protocol
	if discovery and not web_app_only:
		_device_discovery(endless=False)
	else:
		log.info("discovery disabled")

	# start task scheduler
	if task_scheduler and not web_app_only:
		_run_task_scheduler(endless=False)
	else:
		log.info("Task scheduler disabled.")

	# load default ip and port from config
	if not address_port:
		conf = Config.get_config()
		address_port = str.format('{}:{}', conf.get('main', 'ip'), conf.get('main', 'port'))

	# run_django.run_django()
	django.setup()
	call_command('runserver', address_port,
				 use_reloader=False)  # use_reloader=False prevent running start function twice


@cli.command('device-discovery')
@click.option('--endless', default=True, type=bool, help="Run in infinite loop (default true).")
def device_discovery(endless):
	"""Start only device discovery function"""
	# handle interrupt signal when user press ctrl+c
	signal.signal(signal.SIGINT, _exit_signal_handler)

	log.info("start device discovery ...")
	_device_discovery(endless)


@cli.command('collect-data')
@click.option('--endless', default=True, type=bool, help="Run in infinite loop (default true).")
def collect_data(endless):
	"""Start only device data collector"""
	log.info("start collecting data ...")
	# handle interrupt signal when user press ctrl+c
	signal.signal(signal.SIGINT, _exit_signal_handler)

	_collect_data(endless)


@cli.command('task-scheduler')
@click.option('--endless', default=True, type=bool, help="Run in infinite loop (default true).")
def task_scheduler(endless):
	"""
	Start only task scheduler.
	"""
	log.info("Start task scheduler ...")
	signal.signal(signal.SIGINT, _exit_signal_handler)

	_run_task_scheduler(endless)


@cli.command('config')
def config():
	"""Edit EspHub configuration"""
	click.edit(filename=Config.CONFIG_NAME)


@cli.command('reset-config')
def reset_config():
	"""Reset the settings to default"""
	# TODO implement configuration reset
	pass


if __name__ == '__main__':
	cli()
