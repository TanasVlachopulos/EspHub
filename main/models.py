from django.db import models

# from Presentation.WebUi.DataAccess import DBA, DAO
from DataAccess import DBA, DAO

class Device(DAO.Device):
    @staticmethod
    def get_all():
        db = DBA.Dba("test.db")
        return db.get_devices()

    @staticmethod
    def get(device_id):
        db = DBA.Dba("test.db")
        return db.get_device(device_id)


class Record(DAO.Record):

    @staticmethod
    def get_all(device_id, limit=20):
        db = DBA.Dba("test.db")
        return db.get_record_from_device(device_id, limit=limit)
