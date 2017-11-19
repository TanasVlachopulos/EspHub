from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from contextlib import contextmanager
from Tools.Log import Log
from Config.Config import Config
from configparser import NoSectionError, NoOptionError

conf = Config.get_config()

try:
	engine = create_engine(conf.get('db', 'connection_string'), convert_unicode=True)
	Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
except (NoSectionError, NoOptionError):
	log = Log.get_logger()
	log.critical("Missing config record 'connection_string' in section [db]. Cannot found path to database file.")

Base = declarative_base()


def init_db():
	"""
	Initialize database from models
	"""
	# import is necessary for load models, without this line tables won't be created !!!
	import DataAccess.DAO
	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)
	log = Log.get_logger()
	log.debug('Initializing database.')


def get_session():
	"""
	Provide session instance, user is responsible for closing instance
	:return: Session instance
	"""
	return Session()


@contextmanager
def keep_session():
	"""
	Provide session for scope of "with" operator
	:return: Session instance
	"""
	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()
