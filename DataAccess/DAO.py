import time


class Device(object):
    def __init__(self, mac, name, ip, provided_func):
        self.mac = mac
        self.name = name
        self.ip = ip
        self.provided_func = provided_func

    def __str__(self):
        return '| ' + self.mac + ' | ' + self.name + ' | ' + self.ip + ' | ' + ';'.join(self.provided_func) + ' |'

    def to_list(self):
        return [self.mac, self.name, self.ip, self.provided_func]


class Record(object):
    def __init__(self, mac, time, type, value):
        self.mac = mac
        self.time = time
        self.type = type
        self.value = value

    def __str__(self):
        return '| ' + self.mac + ' | ' + time.asctime(time.localtime(self.time)) + ' | ' + self.type + ' | ' + self.value + '|'
