from DatabaseAccess import *
from Commands import *
import time

db = DatabaseAccess('test.db')

device = DAO.Device('222:22:33:99:66:11', 'unknown_device', '10.10.0.1', ['temp', 'analog'])
print(device.to_list())
msg = ['@hello', '10.10.0.12', '222:22:33:99:66:11', 'test_device']
func = command_dic[msg[0]]
func(msg)
msg = ["@provided_func", '222:22:33:99:66:11', 'analog', 'radiation']
func = command_dic[msg[0]]
func(msg)
msg = ['@record', '222:22:33:99:66:11', 'analog', '3.33']
func = command_dic[msg[0]]
func(msg)
# db.insert_device(device)
[print(x) for x in db.get_devices()]
# record = DAO.Record('66:22:33:99:66:111111', time.time(), 'temp', '32.2')
# db.insert_record(record)
[print(x) for x in db.get_record_from_device('222:22:33:99:66:11')]

