import pandas as pd
import numpy as np
from datetime import datetime

offset_mapper = {'minutely': 'T',
				 'hourly': 'H',
				 'daily': 'D',
				 'weekly': 'W',
				 'monthly': 'M'}

def resample_data_vectors(data, index_name, resampling_period):
	"""
	Resample data vectors to given resampling period.
	:param data: Dictionary of data in format: {'vector1': ['2017-12-10 20:00:00', '2017-12-10 20:00:00', '2017-12-10 20:00:00'], 'vector2': [1, 5, 8]}
	:param index_name: Name of key which contain time index, this key must have list of datetime object as value.
	:param resempling_period: One of resampling option: minutely, hourly, daily, weekly, monthly
	:return: Dictionary of in same format as data
	"""
	data_frame = pd.DataFrame(data)
	data_frame[index_name] = pd.to_datetime(data_frame[index_name])
	data_frame = data_frame.set_index(index_name)

	offset = offset_mapper.get(resampling_period, 'minutely')
	data_frame = data_frame.resample(offset).mean()

	# print(data_frame.index.values)
	result = data_frame.to_dict(orient='list')
	result[index_name] = [item.to_pydatetime() for item in data_frame.index.tolist()]
	return result