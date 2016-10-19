"""
========= DATABASE ACCESS ===========
    - handle database connection
    - provides methods for access to database like Insert and Select which returns Database objects
"""

import sqlite3 as sql
import DataAccess.DAO as DAO
import sys


class Dba(object):
    """ Save path to DB file and create tables if not exists """
    def __init__(self, path):
        self._path = path
        con = self._get_connection()
        try:
            cur = con.cursor()
            cur.execute("CREATE TABLE IF NOT EXISTS Devices(Mac TEXT PRIMARY KEY, Name TEXT, Ip TEXT, Provided_func TEXT)")
            cur.execute("CREATE TABLE IF NOT EXISTS Records(Id INTEGER PRIMARY KEY, Mac TEXT, Time NUMERIC, Type TEXT, Value TEXT)")
        except sql.Error as e:
            if con:
                con.rollback()
                con.close()
            print("DB error: ", e.args[0])

    """ Get connection object """
    def _get_connection(self):
        return sql.connect(self._path)

    """ Get list of all devices """
    def get_devices(self):
        con = self._get_connection()
        try:
            cur = con.cursor()
            cur.row_factory = sql.Row  # return data from cursor as dictionary
            cur.execute("SELECT * FROM Devices")
            rows = cur.fetchall()
            return [DAO.Device(x['Mac'], x['Name'], x['Ip'], x['Provided_func'].split(';')) for x in rows]
        except sql.Error as e:
            print(e.args[0])
            return None
        finally:
            con.close()

    """ Get single device by Mac address """
    def get_device(self, mac_address):
        con = self._get_connection()
        try:
            cur = con.cursor()
            cur.row_factory = sql.Row
            cur.execute("SELECT * FROM Devices WHERE Mac=:Mac", {'Mac': mac_address})
            row = (cur.fetchall())[0]  # get first record
            return DAO.Device(row['Mac'], row['Name'], row['Ip'], row['Provided_func'].split(';'))
        except sql.Error as e:
            print(e.args[0])
            return None
        except IndexError:  # when does not exist any record with given mac
            return None
        finally:
            con.close()

    """ Insert singe device to DB """
    def insert_device(self, device):
        con = self._get_connection()
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO Devices(Mac, Name, Ip, Provided_func) VALUES (:Mac, :Name, :Ip, :Provided_func)",
                        {'Mac': device.mac, 'Name': device.name, 'Ip': device.ip,
                         'Provided_func': ';'.join(device.provided_func)})
            con.commit()
        except sql.Error as e:
            print(e.args[0])
        finally:
            con.close()

    """ Update list of provided function for one device """
    def update_provided_func(self, mac, function):
        con = self._get_connection()
        try:
            cur = con.cursor()
            cur.execute("UPDATE Devices SET Provided_func=:provided_func WHERE Mac=:mac",
                        {'provided_func': ';'.join(function), 'mac': mac})
            con.commit()
        except sql.Error as e:
            print(e.args[0])
        finally:
            con.close()

    """ Get all record from single device """
    def get_record_from_device(self, device_mac):
        con = self._get_connection()
        try:
            cur = con.cursor()
            cur.row_factory = sql.Row  # return data from cursor as dictionary
            cur.execute("SELECT * FROM Records WHERE Mac=:Mac",
                        {"Mac": device_mac})
            rows = cur.fetchall()
            return [DAO.Record(x['Mac'], x['Time'], x['Type'], x['Value']) for x in rows]
        except sql.Error as e:
            print(e.args[0])
            return None
        finally:
            con.close()

    """ Insert device record """
    def insert_record(self, record):
        con = self._get_connection()
        try:
            cur = con.cursor()
            cur.execute("INSERT INTO Records(Mac, Time, Type, Value) VALUES(:Mac, :Time, :Type, :Value)",
                        {'Mac': record.mac, 'Time': record.time, 'Type': record.type, 'Value': record.value})
            con.commit()
        except sql.Error as e:
            print(e.args[0])
        finally:
            con.close()