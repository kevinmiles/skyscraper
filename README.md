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

To have a delay between subsequent requests, set the following environment
variable to the number of seconds you want to wait. The actual wait time will
be between 50% and 150% of the given value.

```
SKYSCRAPER_DOWNLOAD_DELAY=5
```


## YAML Spider File

For simple use cases, the spider YAML file can be used to define the whole
scraping process. It allows mainly three actions the scraper can take:

- `follow`: Follow links and continue scraping there
- `extract`: Extract structured information and save to a result file
- `download`: Download some links as a raw file (e.g. images)

The example below shows a simple example of a scraper that visits Wikipedia,
follows the links on the main page and stores these article pages. This
is just an example. If you actually plan to use Wikipedia data, please use
[their XML dumps](https://dumps.wikimedia.org/).

```yaml
engine: requests
start_urls:
  - https://en.wikipedia.org/wiki/Main_Page
rules:
  start_urls:
    stores_item: false
    follow:
      - selector: '#mp-left a::attr(href)'
        next: article_urls
  article_urls:
    extract:
      # Extract structured data with these selectors and stores them to the
      # 'data' field of an item
      - selector: 'h1#firstHeading'
        field: 'title'
```

In this example `rules` defines the actions the scraper should take (follow,
extract or download). Rules are always associated with a specific ruleset name.
The scraper always starts with the URLs defined by `start_urls` and performs
the actions defined by the `start_urls` ruleset. In this case the spider will
follow some links.

The definition `next: article_urls` defines that the
ruleset for the next pages is `article_urls`. The ruleset `article_urls`
tells Skyscraper to extract the title of the page. The extracted data will
be saved to a JSON result file.


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
