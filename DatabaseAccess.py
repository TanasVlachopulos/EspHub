from DataAccess import *


""" singleton provided database instance """
class DatabaseAccess(object):
    _db = None

    def __new__(cls, *args, **kwargs):
        if not DatabaseAccess._db:
            DatabaseAccess._db = DBA.Dba(args[0])
        return DatabaseAccess._db
