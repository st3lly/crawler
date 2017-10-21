from bs4 import BeautifulSoup
import os

class Parser(object):
	def __init__(self):
		pass



def main():
	file = '/home/st3lly/crawler/cars/1000 - skoda-octavia-combi-1-9-tdi-classic-77kw-m5-5d'
	print (file)
	handle = open(file, "rb")
	html = handle.read()
	soup = BeautifulSoup(html, 'html.parser')
	


if __name__ == '__main__':
    main()