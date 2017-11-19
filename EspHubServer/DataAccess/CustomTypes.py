import sqlalchemy.types as types
import json

class CustomStringJson(types.TypeDecorator):
	impl = types.TEXT

	def process_bind_param(self, value, dialect):
		if value is not None:
			try:
				value = json.dumps(value)
			except json.JSONDecodeError:
				raise ValueError("Cannot store JSON in invalid format into database.")
		return value

	def process_result_value(self, value, dialect):
		if value is not None:
			try:
				value = json.loads(value)
			except json.JSONDecodeError:
				raise ValueError("Cannot load JSON in invalid format from database.")
		return value

CustomJson = types.JSON().with_variant(CustomStringJson, 'sqlite')
