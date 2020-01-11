#!/usr/bin/env python

from setuptools import setup

extras = {
    'aws': ['boto3'],
    'mqtt': ['paho-mqtt'],
    'redis': ['redis'],
    'chrome': ['pyppeteer'],
}
extras['all'] = [package for packages in extras.values()
                 for package in packages]

setup(
    name='skyscraper',
    version='0.1.1',
    description='Targeted Crawler/Scraper for molescrape.com',
    author='Stefan Koch',
    author_email='contact@molescrape.com',
    packages=[
        'skyscraper',
        'skyscraper.pipelines',
        'skyscraper.spiders',
    ],
    install_requires=[
        'python-dotenv',
        'scrapy',
        'click',
        'pyyaml',
        'prometheus_client',
        # pandas + beautifulsoup + html5lib used for reading tabular data
        'pandas',
        'beautifulsoup4',
        'html5lib',
        'requests',
        'cloudscraper',
    ],
    extras_require=extras,
    entry_points='''
        [console_scripts]
        skyscraper=skyscraper.commands:skyscraper_service
        skyscraper-spider=skyscraper.commands:skyscraper_spider
        skyscraper-spider-yml=skyscraper.commands:skyscraper_spider_yml
        skyscraper-archive=skyscraper.commands:skyscraper_archive
    ''',
)
