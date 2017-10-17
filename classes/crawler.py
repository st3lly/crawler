from bs4 import BeautifulSoup
import requests
import os
import re
import time

class Crawler(object):

	def __init__(self, url, directory, quiet, limit = 1):
		self.__baseUrl = url + '?p[order]=23&p[page]='
		# add '/' to end of directory name if it doesn't exists
		if directory.endswith('/'):
			self.__dir = directory
		else:
			self.__dir = directory + '/'
		# add current working directory to start of the path if '/' doesn't exists
		if not self.__dir.startswith('/'):
			self.__dir = os.getcwd() + '/' + self.__dir
		self.__quiet = quiet
		self.__limit = limit
		self.__urlList = []

	def log(self, string):
		if self.__quiet != 1:
			print(string)
		else:
			return

	def getUrlList(self):
		self.log('Obtaining URLs...')
		for page in range(1, self.__limit + 1):
			response = requests.get(self.__baseUrl + str(page))
			html = response.text
			soup = BeautifulSoup(html, 'html.parser')
			for div in soup.findAll('div', {'class': 'item-heading'}):
				link = div.find('a')
				href = link.get('href')
				title = link.string
				self.__urlList.append(href)
				self.log('Otained url: ' + href)
			time.sleep(0.5)

	def downloadContent(self):
		self.log('Downloading HTML files...')
		prefix = 0
		for url in self.__urlList:
			response = requests.get(url)
			html = response.text
			soup = BeautifulSoup(html, 'html.parser')
			title = soup.find('h1', {'class': 'header__title'})
			if title == None:
				continue
			title = re.sub('\?|\.|\!|\/|\;|\:', '', title.string)
			file = self.__dir + str(prefix) + ' - ' + title
			if not os.path.exists(file):
				handle = open(file, "w")
				self.log('Downloaded file: ' + file)
				handle.write(html)
				handle.close()
			prefix += 1
			time.sleep(0.5)
			