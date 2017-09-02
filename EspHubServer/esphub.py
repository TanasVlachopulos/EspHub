from django.core.management import call_command
from django.core.management.commands.runserver import BaseRunserverCommand
from Config import Config
from DeviceCom import DataCollector as Collector
from DeviceCom import EspDiscovery as Discovery
from Scheduler import PeriodicDisplayTask
# from .. import run_django
import threading
import django
import os
import sys
import json
import time
import click
import signal

# Variable for PeriodicDisplay task, is global due to signal_handling
task_to_stop = []


class HackedRunserver(BaseRunserverCommand):
    def inner_run(self, *args, **options):
        print('before runserver')
        super(HackedRunserver, self).inner_run(*args, **options)
        print('after runserver')


def _exit_signal_handler(signal, frame):
    print("Interrupt !!!")
    for task in task_to_stop:
        print('stopping task')
        task.stop()

    # raise keyboard interrupt again for stopping Django webserver
    raise KeyboardInterrupt


def _device_discovery(endless=True):
    """
    Start device discovery function
    :param endless: run discovery in endless loop (default true)
    :return: 
    """
    conf = Config.Config().get_config()

    msg = json.dumps({"name": conf.get('mqtt', 'server_name'),
                      "ip": conf.get('mqtt', 'ip'),
                      "port": conf.getint('mqtt', 'port')})

    run_event = threading.Event()
    run_event.set()

    esp_discovery = Discovery.EspDiscovery(conf.get('discovery', 'broadcast'),
                                           conf.getint('discovery', 'port'),
                                           msg,
                                           conf.getint('discovery', 'interval'),
                                           run_event)
    try:
        esp_discovery.start()

        if endless:
            while True:
                time.sleep(0.5)

    except KeyboardInterrupt or SystemExit:
        run_event.clear()
        esp_discovery.join()
        click.echo("Process terminated")


def _collect_data(endless=True):
    """
    Start collecting data from devices
    :param endless: run collecting iin endless loop (default true)
    :return: 
    """
    conf = Config.Config().get_config()

    Collector.DataCollector(conf.get('db', 'path'), 'config')

    if endless:
        try:
            while True:
                time.sleep(0.5)
        except KeyboardInterrupt:
            click.echo("Process terminated")
            exit(0)


@click.group()
def cli():
    """EspHub home automation server"""
    # magic with system path
    sys.path.append('..')
    sys.path.append('/WebUi')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebUi.settings')


@cli.command()
@click.option('--discovery/--no-discovery', default=True, help='Device discovery function (default enable)')
@click.option('--collecting/--no-collecting', default=True, help='Collecting data from devices (default enable)')
@click.option('--web-app-only/--full-app', default=False,
              help='Run only web interface without other functions (default disabled)')
@click.argument('address-port', default='', metavar='[ipaddr:port]')
def start(discovery, collecting, web_app_only, address_port):
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
        click.echo("collecting disabled")

    # start discovery protocol
    if discovery and not web_app_only:
        _device_discovery(endless=False)
    else:
        click.echo("discovery disabled")

    # load default ip and port from config
    if not address_port:
        conf = Config.Config().get_config()
        address_port = str.format('{}:{}', conf.get('main', 'ip'), conf.get('main', 'port'))

    # start task scheduler
    task = PeriodicDisplayTask.PeriodicDisplayTask()
    task.start()
    task_to_stop.append(task)

    # run_django.run_django()
    django.setup()
    call_command('runserver', address_port,
                 use_reloader=False)  # use_reloader=False prevent running start function twice


@cli.command('device-discovery')
@click.option('--endless', default=True, type=bool, help="Run in infinite loop (default true)")
def device_discovery(endless):
    """Start only device discovery function"""
    click.echo("start device discovery ...")
    _device_discovery(endless)


@cli.command('collect-data')
@click.option('--endless', default=True, type=bool, help="Run in infinite loop (default true)")
def collect_data(endless):
    """Start only device data collector"""
    click.echo("start collecting data ...")
    _collect_data(endless)


@cli.command('config')
def config():
    """Edit EspHub configuration"""
    click.edit(filename=Config.Config().CONFIG_PATH)


@cli.command('reset-config')
def reset_config():
    """Reset the settings to default"""
    # TODO implement configuration reset
    pass


if __name__ == '__main__':
    cli()
