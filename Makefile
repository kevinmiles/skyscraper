SHELL := /bin/bash

setup-dev:
	virtualenv env
	source env/bin/activate && pip install -e .[all] && pyppeteer-install

test:
	rm -r /tmp/skyscraper && mkdir /tmp/skyscraper
	tox
	source integration-tests/dotenv && export $$(cut -d= -f1 integration-tests/dotenv | grep -v '^$$') && bats integration-tests/
