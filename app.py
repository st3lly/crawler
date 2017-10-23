import click
from classes.crawler import Crawler
from classes.parser import Parser
import os
from elasticsearch import Elasticsearch

@click.command()
@click.option('--p', default = 1)
@click.option('--f', default = 1)
@click.option('--d', type = click.Path(exists = True), default = os.getcwd())
@click.option('--q', default = 0)
@click.option('--o', type = click.Choice(['0', '1', '2']), default = '2')
def main(p, d, q, f, o):
	doCrawler = True
	doParser = True
	if o == '0':
		doParser = False
	elif o == '1':
		doCrawler = False

	dir_ = ''
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
	if d.endswith('\\'):
		dir_ = d
	else:
		dir_ = d + '\\'
	# add current working directory to start of the path if '/' doesn't exists
	if not dir_.startswith('\\'):
		dir_ = os.getcwd() + '\\' + dir_

	if doCrawler:
		if q == 0:
			print('Crawling was started...')
			print('---------------------------------')
		c = Crawler('https://osobne-auta.autobazar.sk/?p[order]=23&p[page]=', dir_, q, p, f)
		c.getUrlList()
		c.downloadContent()
	if doParser:
		if q == 0:
			print('Parsing was started...')
			print('---------------------------------')
		files = [dir_ + f for f in os.listdir(dir_)]
		es = Elasticsearch()
		p = Parser(es, q)
		p.parseData(files)

if __name__ == '__main__':
    main()
