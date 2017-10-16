from bs4 import BeautifulSoup
import requests

class Crawler(object):

	def __init__(self, url, limit = 1):
		self.__baseUrl = url + '?p[order]=23&p[page]='
		self.__limit = limit

	def crawlContent(self):
		for page in range(1, self.__limit + 1):
			response = requests.get(self.__baseUrl + str(page))
			html = response.text
			soup = BeautifulSoup(html, 'html.parser')
			for div in soup.findAll('div', {'class': 'item-heading'}):
				link = div.find('a')
				href = link.get('href')
				title = link.string
				print(title)

if __name__ == '__main__':
    print('Crawling was started...')
    c = Crawler('https://osobne-auta.autobazar.sk/', 10)
    c.crawlContent()