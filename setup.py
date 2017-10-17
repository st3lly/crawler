from setuptools import setup

setup(
    name = 'crawler',
    version = '0.1',
    author = 'Stefan Kadlic',
    author_email = 'st3lly1@gmail.com',

    description = 'Crawler for download all data about cars from website autobazar.sk',
    url = 'https://github.com/st3lly/crawler',
    license = 'MIT',
    zip_safe = False,

    entry_points={
        'console_scripts': [
            'crawler = app:main'
        ]
    },
)