"""
============= DATABASE ACCESS OBJECTS ===============
    -   maps database entities to object representation
"""
import time
import json
import datetime


class Device(object):
    def __init__(self, id, name, provided_func):
        self.id = id
        self.name = name
        self.provided_func = provided_func

    def __str__(self):
        return '| ' + self.id + ' | ' + self.name + ' | ' + self.provided_func + ' |'

    def to_list(self):
        return [self.id, self.name, self.provided_func]


class Record(object):
    def __init__(self, id, time, value_type, value):
        """

        :param id: unique device id - string value
        :param time: primarily in Datetime format but accept also UNIX timestamp in float and int format
        :param value_type:
        :param value:
        """
        self.id = id
        if type(time) is float or type(time) is int:
            self._time = time
        else:
            self._time = time.timestamp()
        self.name = value_type
        self.value = value

    @property
    def timestamp(self):
        return self._time

    @property
    def time(self):
        return datetime.datetime.fromtimestamp(self._time)

    @time.setter
    def time(self, value):
        self._time = value.timestamp()

    def __str__(self):
        return '| ' + self.id + ' | ' + str(self._time) + ' | ' + self.name + ' | ' + self.value + '|'


class Telemetry(object):
    def __init__(self, device_id, time, rssi='0', heap='0', cycles='0', voltage='0', ip='0', mac='0', ssid='0'):
        """
        Holder of device telemetry
        :param device_id: unique device id - string value
        :param time: primarily in Datetime format but accept also UNIX timestamp in float and int format
        :param rssi: Recieved signa code power to wifi AP
        :param heap: Amount of memory on heap
        :param cycles:
        :param voltage: Device input voltage
        :param ip: Device IP address
        :param mac: Device MAC address
        """
        self.device_id = device_id
        if type(time) is float or type(time) is int:
            self._time = time
        else:
            self._time = time.timestamp()
        self.rssi = rssi
        self.heap = heap
        self.cycles = cycles
        self.voltage = voltage
        self.ip = ip
        self.mac = mac
        self.ssid = ssid

    @property
    def timestamp(self):
        return self._time

    @property
    def time(self):
        return datetime.datetime.fromtimestamp(self._time)

    @time.setter
    def time(self, value):
        self._time = value.timestamp()

    def __str__(self):
        return str.format("{} | {} | {} | {} | {} | {} | {}",
                          self.device_id, self.time, self.rssi, self.heap, self.cycles, self.voltage, self.ip, self.mac, self.ssid)


class Ability(object):
    def __init__(self, name='', user_name='', io='', category='', unit='', default_value=0, desc=''):
        self.name = name
        self.user_name = user_name
        self.io = io
        self.category = category
        self.unit = unit
        self.default_value = default_value
        self.desc = desc

    def init_with_json(self, json_str):
        obj = json.loads(json_str)
        self.name = obj.get('name', '')
        self.user_name = obj.get('user_name', '')
        self.io = obj.get('io', '')
        self.category = obj.get('category', '')
        self.unit = obj.get('unit', '')
        self.default_value = obj.get('default_value', 0)
        self.desc = obj.get('desc', '')

    def to_json(self):
        json.dumps(self.__dict__)

    def __str__(self):
        return str.format("{} | {} | {} | {} | {} | {} | {}",
                          self.name, self.user_name, self.io, self.category, self.unit, self.default_value, self.desc)


class Display(object):
    """
    Hold information about one display screen
    :param id: Display unique ID - Number
    :param device_id: ID of parent device - Text
    :param display_name: name of device ability - Text
    :param screen_number: ID of display screen - Number
    :param params: additional settings in JSON format - Text 
    """
    def __init__(self, **kwargs):
        self._id = kwargs.get('id')
        self.device_id = kwargs.get('device_id', '')
        self.display_name = kwargs.get('display_name', '')
        self.screen_nuber = kwargs.get('screen_number', 0)
        self.params = kwargs.get('params', '')

    def __str__(self):
        return str.format("{} | {} | {} | {} | {}",
                          str(self._id), self.device_id, self.display_name, str(self.screen_nuber), self.params)