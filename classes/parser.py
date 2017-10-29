from bs4 import BeautifulSoup
import os
import io
import re
from json import dumps
from elasticsearch import helpers
from geopy.geocoders import Nominatim

class Parser(object):
	def __init__(self, es, q, idFrom):
		self.__json_car = {}
		self.__es = es
		self.__quiet = q
		self.__idFrom = idFrom

	def log(self, string):
		if self.__quiet != 1:
			print(string)
		else:
			return

	def parseData(self, files):
		id_ = self.__idFrom
		actions = []
		for file in files:
			self.log('Parsing file [id: ' + str(id_) + ']: ' + file)
			with io.open(file, mode = 'r', encoding = 'utf-8') as handle:
				soup = BeautifulSoup(handle.read(), 'html.parser')

				self.__json_car['make'] = None
				self.__json_car['model'] = None
				self.__json_car['price'] = None
				self.__json_car['title'] = None
				self.__json_car['date_of_production'] = None
				self.__json_car['state'] = None
				self.__json_car['mileage'] = None
				self.__json_car['fuel'] = None
				self.__json_car['cubic_capacity'] = None
				self.__json_car['power'] = None
				self.__json_car['gearbox'] = None
				self.__json_car['body'] = None
				self.__json_car['drive'] = None
				self.__json_car['color'] = None
				self.__json_car['safety'] = None
				self.__json_car['comfort'] = None
				self.__json_car['other_equipment'] = None
				self.__json_car['more_details'] = None
				self.__json_car['notes'] = None
				self.__json_car['address'] = None
				self.__json_car['location'] = {}
				self.__json_car['location']['lat'] = 0
				self.__json_car['location']['lon'] = 0

				title = soup.find('h1', {'class': 'header__title'})
				if title is not None:
					self.__json_car['title'] = title.string
				else:
					continue # if doesn't exist title, car was deleted from the website, therefore continue

				price = soup.find('h1', {'class': 'price__amount'})
				if price is not None:
					price = re.sub("\D", "", price.string)
					self.__json_car['price'] = price

				#make and model
				menuLinks = soup.findAll('a', {'data-ga-event-new' : 'clickWithPageCategoryLabel'})
				try:
					make = menuLinks[2].get_text().strip()
					self.__json_car['make'] = make
				except:
					pass

				try:
					model = menuLinks[3].get_text().strip()
					model = model.replace(make, '').lstrip()
					self.__json_car['model'] = model
				except:
					pass

				# basic values are always on firt 9 positions (0 - 8)
				basicValues = soup.findAll('p', {'class': 'parameters__value'})
				basicValuesLabel = soup.findAll('span', {'class': 'parameters__label'})
				#for label in basicValuesLabel:
					#if label.string == 'Rok výroby:'
				for i in range(len(basicValues)):
					if basicValuesLabel[i].string == 'Rok výroby:':
						self.__json_car['date_of_production'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Stav:':
						self.__json_car['state'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Najazdené:':
						mileage = re.sub("\D", "", basicValues[i].string)
						self.__json_car['mileage'] = mileage
					elif basicValuesLabel[i].string == 'Palivo:':
						self.__json_car['fuel'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Objem:':
						p = re.compile(r'\([^)]*\)')
						cubic_capacity = re.sub(p, '', basicValues[i].string)
						cubic_capacity = re.sub("\D", "", cubic_capacity)
						self.__json_car['cubic_capacity'] = cubic_capacity
					elif basicValuesLabel[i].string == 'Výkon:':
						p = re.compile(r'\([^)]*\)')
						power = re.sub(p, '', basicValues[i].string)
						power = re.sub("\D", "", power)
						self.__json_car['power'] = power
					elif basicValuesLabel[i].string == 'Prevodovka:':
						self.__json_car['gearbox'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Karoséria:':
						self.__json_car['body'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Pohon:':
						self.__json_car['drive'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Farba:':
						self.__json_car['color'] = basicValues[i].string

				sections = soup.findAll('section', {'class': 'tab__section'})
				for section in sections:
					tabTitle = section.find('h2', {'class': 'tab__title'}).string
					if(tabTitle == 'Bezpečnosť'):
						safety = section.findAll('li', text = True)
						self.__json_car['safety'] = ', '.join(i.string for i in safety)
					elif(tabTitle == 'Komfort'):
						comfort = section.findAll('li', text = True)
						self.__json_car['comfort'] = ', '.join(i.string for i in comfort)
					elif(tabTitle == 'Dalšia výbava'):
						other_equipment = section.findAll('li', text = True)
						self.__json_car['other_equipment'] = ', '.join(i.string for i in other_equipment)
					elif(tabTitle == 'Dalšie informácie'):
						more_details = section.findAll('li', text = True)
						self.__json_car['more_details'] = ', '.join(i.string for i in more_details)
					elif(tabTitle == 'Poznámka'):
						notes = section.findAll('p', text = True)
						self.__json_car['notes'] = ', '.join(i.string for i in notes)

				address = soup.find('dd', {'class': 'information__value'})
				if address is not None:
					self.__json_car['address'] = address.string.strip()
					geolocator = Nominatim()
					try:
						location = geolocator.geocode(self.__json_car['address'])
						self.__json_car['location']['lat'] = location.latitude
						self.__json_car['location']['lon'] = location.longitude
					except:
						pass

				actions.append(
					{
						'_index': 'autobazar',
						'_type': 'car',
						'_id': id_,
						'_source': dumps(self.__json_car, ensure_ascii = False)
	                }
	            )
				id_ += 1
				if id_ % 1000 == 0:
					helpers.bulk(self.__es, actions, chunk_size = 1000, request_timeout = 200)
					actions.clear()

		helpers.bulk(self.__es, actions, chunk_size = 1000, request_timeout = 200)
