from bs4 import BeautifulSoup
import os
import io
import re
from json import dumps
from elasticsearch import helpers

class Parser(object):
	def __init__(self, es, q):
		self.__json_car = {}
		self.__es = es
		self.__quiet = q

	def log(self, string):
		if self.__quiet != 1:
			print(string)
		else:
			return

	def parseData(self, files):
		id_ = 0
		actions = []
		for file in files:
			self.log('Parsing file [id: ' + str(id_) + ']: ' + file)
			with io.open(file, mode = 'r', encoding = 'utf-8') as handle:
				soup = BeautifulSoup(handle.read(), 'html.parser')

				self.__json_car['title'] = None
				title = soup.find('h1', {'class': 'header__title'})
				if title is not None:
					self.__json_car['title'] = title.string
				else:
					continue # if doesn't exist title, car was deleted from the website, therefore continue

				self.__json_car['price'] = None
				price = soup.find('h1', {'class': 'price__amount'})
				if price is not None:
					price = re.sub("\D", "", price.string)
					self.__json_car['price'] = price

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
						self.__json_car['mileage'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Palivo:':
						self.__json_car['fuel'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Objem:':
						self.__json_car['cubic_capacity'] = basicValues[i].string
					elif basicValuesLabel[i].string == 'Výkon:':
						self.__json_car['power'] = basicValues[i].string
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

				actions.append(
					{
						'_index': 'autobazar',
						'_type': 'car',
						'_id': id_,
						'_source': dumps(self.__json_car, ensure_ascii = False)
	                }
	            )
				id_ += 1

		helpers.bulk(self.__es, actions, chunk_size = 1000, request_timeout = 200)
