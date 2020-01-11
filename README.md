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

Set the following environment variables to define where scraped data and
downloaded files should be stored:

```
SKYSCRAPER_STORAGE_FOLDER_PATH=/data/skyscraper=items
SKYSCRAPER_STORAGE_DOWNLOADS_PATH=/data/skyscraper-downloads
```


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
* add a `--verbose` mode which outputs current URL, found items, found links
* use relative imports
* use requests `Session` to manage cookies (handle cookies in a wrapper
  layer which is the same for all engines, so that e.g. a switch between
  Chrome engine and file downloader uses the same cookies)
