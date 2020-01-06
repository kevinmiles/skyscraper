# Skyscraper

Skyscraper is the scraping engine of molescrape. It can perform targeted
crawls for specific data in defined intervals.


## Documentation

The full user documentation can be found at
[docs.molescrape.com](https://docs.molescrape.com/). This README file is
designed to be a quick overview.


## Usage

There is a command line interface that can be used to run crawls. For daemon
operation run the following command. This will start a daemon that will
execute your spiders according to the defined schedule:

```bash
python -m skyscraper --daemon
```

To run a single spider manually use

```bash
python -m skyscraper --spider spider.yml
```

with `spider.yml` being the path to your spider's YAML configuration file.


## TODO

* Add a default scraper that stores full HTML for a page and scrapes the
  whole domain from a start URL
* Make molescrape so simple that somebody wants to use it
  * probably I can get rid of scrapy, because I do not need parallelism and
    it complicates stuff like downloading files
  * getting started: command to start program + URL to start scraping
* Configurable with:
  * URL
  * Selector to follow -> if new, load and possibly download a file
* create `skyscraper/__main__.py` so that `python -m skyscraper --help` works
