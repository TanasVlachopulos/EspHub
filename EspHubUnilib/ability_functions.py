import requests
from requests.exceptions import MissingSchema

api_key = '329ebdde6a21374afda028d45dcb0519'


def get_temperature(city_code):
	url = "http://api.openweathermap.org/data/2.5/weather?id={}&units=metric&appid={}".format(city_code, api_key)
	try:
		r = requests.get(url)
		response = r.json()
		return response['main']['temp']
	except MissingSchema:
		print("Error: request failed.")
	except KeyError:
		print("Error: incomplete response.")


def weather_karvina():
	return get_temperature('3073789')


def weather_trinec():
	return get_temperature('3064000')
