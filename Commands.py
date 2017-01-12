from DatabaseAccess import *
import time

""" ############# OBSOLETE ############# """
""" receive transmission from new device """
""" check if exists record in DB and add device to DB """
def new_device(args):
    db = DatabaseAccess()
    if not db.get_device(args[2]):
        db.insert_device(DAO.Device(args[2], args[3], args[1], []))


def new_provided_functions(args):
    db = DatabaseAccess()
    if db.get_device(args[1]):
        db.update_provided_func(args[1], [args[x] for x in range(2, len(args))])

def new_record(args):
    db = DatabaseAccess()
    record = DAO.Record(args[1], time.time(), args[2], args[3])
    db.insert_record(record)

command_dic = {'@hello': new_device,
               '@provided_func': new_provided_functions,
               '@record': new_record}
