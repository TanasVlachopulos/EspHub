from django.core.management import call_command
from Config import Config
from DeviceCom import DataCollector as Collector
from DeviceCom import EspDiscovery as Discovery
import django
import os
import sys
import json
import time
import click


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

    esp_discovery = Discovery.EspDiscovery(conf.get('discovery', 'broadcast'),
                                           conf.getint('discovery', 'port'),
                                           msg,
                                           conf.getint('discovery', 'interval'))
    esp_discovery.start()

    if endless:
        try:
            while True:
                time.sleep(0.2)
        except KeyboardInterrupt:
            exit(0)


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
                time.sleep(0.2)
        except KeyboardInterrupt:
            exit(0)


@click.group()
def cli():
    """EspHub home automatization server"""
    sys.path.append('/WebUi')
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebUi.settings')


@cli.command()
@click.option('--discovery/--no-discovery', default=True, help='Device discovery function (default enable)')
@click.option('--collecting/--no-collecting', default=True, help='Collecting data from devices (default enable)')
@click.argument('address-port', default='', metavar='[ipaddr:port]')
def start(discovery, collecting, address_port):
    """
    Start EspHub server with all functions
    
    \b
    Arguments:
        ipaddr:port     Optional port number, or ipaddr:port
    """
    if discovery:
        _device_discovery(endless=False)
    else:
        click.echo("discovery disabled")

    if collecting:
        _collect_data(endless=False)
    else:
        click.echo("collecting disabled")

    click.echo("Start server")

    # load default ip and port from config
    if not address_port:
        conf = Config.Config().get_config()
        address_port = str.format('{}:{}', conf.get('main', 'ip'), conf.get('main', 'port'))

    django.setup()
    call_command('runserver', address_port, use_reloader=False)  # use_reloader=False prevent running start function twice


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
