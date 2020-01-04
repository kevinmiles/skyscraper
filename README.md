# Skyscraper

Skyscraper is the scraping engine of molescrape. It can perform targeted
crawls for specific data in defined intervals.


## Documentation

The full user documentation can be found at
[docs.molescrape.com](https://docs.molescrape.com/). This README file is
designed to be a quick overview.


## Usage

There is a command line client that can be used to run crawls. For server
operation, run the following command. This will start a process that will
execute your spiders whenever required:

```bash
skyscraper
```

To run a spider manually, use

```bash
skyscraper-spider [namespace] [spider]
```

with the namespace and the name of the spider.


## Development

You can quickly setup a development environment with

```bash
make setup-dev
```

This will setup a *virtualenv* in the folder `env` with all packages for
all features and an already downloaded Chrome headless setup.

To start working switch to the virtual environment with
`source env/bin/activate`. You can execute the tests with `make test`.


## TODO

* Add a default scraper that stores full HTML for a page and scrapes the
  whole domain from a start URL
