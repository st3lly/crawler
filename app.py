import click
from classes.crawler import Crawler
import os

@click.command()
@click.option('--p', default = 1)
@click.option('--d', type = click.Path(exists = True), default = os.getcwd())
@click.option('--q', default = 0)
def main(p, d, q):
	if q == 0:
		print('Crawling was started...')
		print('---------------------------------')
	c = Crawler('https://osobne-auta.autobazar.sk/', d, q, p)
	c.getUrlList()
	c.downloadContent()

if __name__ == '__main__':
    main()