from bs4 import BeautifulSoup
import requests
import os
import time
import sys
import io

class Crawler(object):

	def __init__(self, url, directory, quiet, limit = 1, startFrom = 1):
		self.__baseUrl = url
		'''
		# add '/' to end of directory name if it doesn't exists
		if directory.endswith('/'):
			self.__dir = directory
		else:
			self.__dir = directory + '/'
		# add current working directory to start of the path if '/' doesn't exists
		if not self.__dir.startswith('/'):
			self.__dir = os.getcwd() + '/' + self.__dir
		'''
		# add '/' to end of directory name if it doesn't exists
		if directory.endswith('\\'):
			self.__dir = directory
		else:
			self.__dir = directory + '\\'
		# add current working directory to start of the path if '/' doesn't exists
		if not self.__dir.startswith('\\'):
			self.__dir = os.getcwd() + '\\' + self.__dir
		self.__quiet = quiet
		self.__limit = limit
		self.__urlList = []
		self.__from = startFrom

	def log(self, string):
		if self.__quiet != 1:
			print(string)
		else:
			return

	def httpRequest(self, req, t = 5):
		while True:
			try:
				return requests.get(req, timeout = t)
			except requests.exceptions.HTTPError as err:
				print(err)
				print('retrying...')
				time.sleep(t)
				continue
			except requests.exceptions.ConnectionError as err:
				print(err)
				print('retrying...')
				time.sleep(t)
				continue
			except requests.exceptions.Timeout as err:
				print(err)
				print('retrying...')
				time.sleep(t)
				continue

	def getUrlList(self):
		self.log('Obtaining URLs...')
		i = 1
		for page in range(self.__from, self.__from + self.__limit):
			response = self.httpRequest(self.__baseUrl + str(page))
			html = response.text
			soup = BeautifulSoup(html, 'html.parser')
			for div in soup.findAll('div', {'class': 'item-heading'}):
				link = div.find('a')
				href = link.get('href')
				title = link.string
				self.__urlList.append(href)
				self.log('Otained url [' + str(i) + ']: ' + href)
				i += 1
			# time.sleep(0.2)

	def downloadContent(self):
		self.log('Downloading HTML files...')
		encoding = 'utf-8'
		prefix = (self.__from - 1) * 20 + 1
		for url in self.__urlList:
			response = self.httpRequest(url)
			html = response.text
			soup = BeautifulSoup(html, 'html.parser')
			parsed_url = url.split('/')
			title = parsed_url[4]
			file = self.__dir + str(prefix) + ' - ' + title
			if not os.path.exists(file):
				with io.open(file, 'w', encoding = encoding) as handle:
					self.log('Downloaded file [' + str(prefix) + ']: ' + file)
					handle.write(html)
					handle.close()
			prefix += 1
			# time.sleep(0.2)
