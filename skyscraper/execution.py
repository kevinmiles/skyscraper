import abc
import os
import subprocess
import datetime
import heapq
import collections
import logging
import prometheus_client
import scrapy
import requests
import pyppeteer.errors
from lxml import html
import urllib.parse
import re

import skyscraper.items
import skyscraper.storage
from .engine import AbstractEngine, Request

from scrapy.exceptions import DropItem
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


SPIDERS_EXECUTED_COUNT = prometheus_client.Counter(
    'skyscraper_executed_spiders',
    'Counter for the number of executed spiders')


class SkyscraperRunner(object):
    def __init__(self, spider_runners):
        self.next_scheduled_runtimes = []
        self.spider_config = collections.defaultdict(dict)

        self.spider_runners = spider_runners

    def update_spider_config(self, configs):
        for config in configs:
            if not config.enabled:
                continue

            if self._has_new_config(config.project, config.spider, config):
                self.spider_config[config.project][config.spider] = config

                # TODO: When pushing a spider due to new configuration
                # all previous schedules of the same spider have to be removed
                # from the schedule (otherwise they will trigger reschedules
                # over and over)
                heapq.heappush(self.next_scheduled_runtimes,
                    (datetime.datetime.utcnow(),
                    (config.project, config.spider)))

    def run_due_spiders(self):
        # heaps are sorted in python
        # https://docs.python.org/3.1/library/heapq.html
        while len(self.next_scheduled_runtimes) > 0 \
                and datetime.datetime.utcnow() > self.next_scheduled_runtimes[0][0]:

            item = heapq.heappop(self.next_scheduled_runtimes)
            project, spider = item[1]

            config = self.spider_config[project][spider]
            engine = config.engine

            SPIDERS_EXECUTED_COUNT.inc()
            runner = self.spider_runners.get(engine, None)
            if not runner:
                raise ValueError('Unknown scraping engine "{}"'.format(engine))

            # TODO: This method should be called run(), but this will require
            # some refactoring on the ScrapySpiderRunner
            options = {'tor': True} if config.use_tor else {}
            runner.run_standalone(project, spider, options)

            self._reschedule_spider(project, spider)

    def _has_new_config(self, project, spider, config):
        try:
            old_conf = self.spider_config[project][spider]
            return hash(config) != hash(old_conf)
        except KeyError:
            # does not exist yet = is new config
            return True

    def _reschedule_spider(self, project, spider):
        try:
            config = self.spider_config[project][spider]

            # if there is a recurrence defined, schedule it again
            if config.recurrence_minutes:
                logging.debug('Rescheduling spider {}/{} in {} min.'.format(
                    project, spider, config.recurrence_minutes))

                next_runtime = datetime.datetime.utcnow() \
                    + datetime.timedelta(minutes=config.recurrence_minutes)
                heapq.heappush(
                    self.next_scheduled_runtimes,
                    (next_runtime, (project, spider)))
        except KeyError:
            # spider was removed, do not schedule again
            pass


class SkyscraperSpiderRunner(object):
    def __init__(self, storage, crawler):
        self.crawler = crawler
        self.items = []
        self.storage = storage

    def run(self, config):
        for item in self.crawler.crawl(config):
            self.storage.store_item(item)


class AbstractCrawler(abc.ABC):
    """Crawlers implement the logic which should be used to
    follow URLs, extract information etc. It does not perform the actual
    request, instead it relies on a crawling engine to achieve this."""

    def __init__(self, engine: AbstractEngine):
        self.engine = engine

    @abc.abstractmethod
    def crawl(self, config):
        pass


class SkyscraperCrawler(AbstractCrawler):
    """Skyscraper crawler is the built-in crawler that uses a YML configuration
    file to define which sites should be crawled and what information should
    be extracted."""

    def __init__(self, engine: AbstractEngine):
        self.engine = engine
        self.backlog = []

    def crawl(self, config):
        for url in config.start_urls:
            self.backlog.append(('start_urls', url))

        while len(self.backlog):
            rule_id, url = self.backlog.pop()

            response = self.engine.perform_request(Request(url))

            if self._stores_items(rule_id, config.rules):
                data = self._run_extractors(rule_id, config.rules, response.text)
                item = skyscraper.items.Item(
                    config.project, config.spider,
                    url=response.url,
                    data=data)

                if rule_id in config.rules \
                        and 'source' in config.rules[rule_id] \
                        and config.rules[rule_id]['source']:
                    item.source = response.text

                yield item

            for url in self._run_downloads(rule_id, config.rules, response.text):
                url = urllib.parse.urljoin(response.url, url)
                content = self.engine.perform_download(url)

                item = skyscraper.items.DownloadItem(
                    config.project, config.spider, bytes=content)

                # TODO: is this heuristics to detect file type OK?
                m = re.match(r'.+\.(\w{2,4})', url)
                if m:
                    item.extension = m[1]

                yield item

            for f in self._run_follows(rule_id, config.rules, response.text):
                level = f[0]
                url = urllib.parse.urljoin(response.url, f[1])
                self.backlog.append((level, url))

    def _run_extractors(self, rule_id, rules, content):
        data = {}

        if rule_id in rules and 'extract' in rules[rule_id]:
            tree = html.fromstring(content)

            for extractor in rules[rule_id]['extract']:
                data[extractor['field']] = self._execute_selector(
                    extractor['selector'], tree)

        return data

    def _run_downloads(self, rule_id, rules, content):
        urls = []

        if rule_id in rules and 'download' in rules[rule_id]:
            tree = html.fromstring(content)

            for extractor in rules[rule_id]['download']:
                urls += self._execute_selector(extractor['selector'], tree)

        return urls

    def _run_follows(self, rule_id, rules, content):
        links = []

        if rule_id in rules and 'follow' in rules[rule_id]:
            tree = html.fromstring(content)

            for extractor in rules[rule_id]['follow']:
                next_level = extractor['next']

                for url in self._execute_selector(extractor['selector'], tree):
                    links.append((next_level, url))

        return links

    def _execute_selector(self, selector, tree):
        base_selector, _, pseudoclass = selector.partition('::')

        elements = tree.cssselect(base_selector)
        return list(map(lambda elem: self._apply_pseudoclass(pseudoclass, elem), elements))

    def _apply_pseudoclass(self, pseudoclass, elem):
        if not pseudoclass:
            return elem.text_content()
        else:
            m = re.match(r'([\w-]+)(?:\(([\w-]+)\))?', pseudoclass)
            if not m:
                raise ValueError('Invalid pseudoclass "{}", could not parse'.format(pseudoclass))
            else:
                if m[1] == 'attr':
                    return elem.get(m[2])
                elif m[1] == 'text':
                    return elem.text_content()
                else:
                    raise ValueError('Unknown pseudoclass "{}"'.format(pseudoclass))

    def _stores_items(self, rule_id, rules):
        if rule_id not in rules:
            return False
        elif 'store_item' not in rules[rule_id]:
            # by default, assume items should be stored
            return True
        else:
            return rules[rule_id]['store_item']


class ScrapySpiderRunner(object):
    """This class is a runner to help with the execution of spiders with
    a given configuration. It sets up the environment and configurations
    and then executes the spider.
    """
    def __init__(self, http_proxy):
        self.http_proxy = http_proxy

    def run_standalone(self, namespace, spider, options={}):
        command = [
            'skyscraper-spider',
            namespace,
            spider,
        ]

        if 'tor' in options and options['tor']:
            command.append('--use-tor')

        subprocess.Popen(command)

    def run(self, namespace, spider, semaphore=None, options={}):
        """Run the given spider with the defined options. Will block
        until the spider has finished.
        """
        if not self._acquire_run_lock(semaphore):
            return

        if 'tor' in options and options['tor']:
            self._set_proxy_tor()

        # Start the spider in this process
        settings = get_project_settings()
        settings['USER_NAMESPACE'] = namespace
        process = CrawlerProcess(settings)
        process.crawl(spider)
        process.start()

        self._release_run_lock(semaphore)

    def _set_proxy_tor(self):
        if not self.http_proxy:
            raise ValueError('No http proxy was configured, but this is '
                             'required if TOR is enabled for a spider')

        # TODO: What happens if we run multiple instances of Skyscraper
        # on one host? Will all of them have http_proxy set if one of them
        # sets it?
        os.environ['http_proxy'] = 'http://{}'.format(self.http_proxy)
        os.environ['https_proxy'] = 'https://{}'.format(self.http_proxy)

    def _acquire_run_lock(self, semaphore):
        if not semaphore:
            return True
        else:
            try:
                semaphore.acquire()
                return True
            except Exception:
                return False

    def _release_run_lock(self, semaphore):
        if semaphore:
            semaphore.release()


class ChromeCrawler(object):
    def __init__(self, settings, browser_future):
        # TODO: Improve the async stuff, we actually only need sync
        # execution
        self.browser_future = browser_future
        self.browser = None
        self.settings = settings

    async def crawl(self, spider):
        # TODO:
        # 1. load spider with spiderloader here
        # 2. read the start urls
        # 3. iterate start urls and emitted requests and run all emitted
        #    BasicItems through the pipeline steps
        if not self.browser:
            self.browser = await self.browser_future
        frontier = spider.start_urls

        results = []
        for url in frontier:
            try:
                page = await self.browser.newPage()
                response = await page.goto(url)

                res = await spider.parse(page, response)
                if isinstance(res, scrapy.Item):
                    results.append(res)
                else:
                    results += res
            except pyppeteer.errors.NetworkError:
                logging.error(
                    'Pyppeteer NetworkError while visiting "{}"'.format(url))

        return results

    async def close(self):
        await self.browser.close()


class ChromeSpiderRunner(object):
    def __init__(self, crawler, spider_loader, pipelines):
        self.crawler = crawler
        self.spider_loader = spider_loader
        self.pipelines = pipelines

    def run_standalone(self, project, spider, options={}):
        # Run in a separate process to mitigate issues with Chrome connection
        # failing and killing the whole service
        command = [
            'skyscraper-spider',
            project,
            spider,
            '--engine',
            'chrome',
        ]

        if 'tor' in options and options['tor']:
            command.append('--use-tor')

        subprocess.Popen(command)

    async def run(self, project, spider):
        # TODO: Improve setting the namespace, should not have to be done
        # during runtime of object
        self.crawler.settings['USER_NAMESPACE'] = project

        spider_class = self.spider_loader.load(spider, namespace=project)
        spider = spider_class()

        pipelines = [self._load_pipeline(p, self.crawler) for p in self.pipelines]

        results = await self.crawler.crawl(spider)
        for item in results:
            for pipeline in pipelines:
                try:
                    item = pipeline.process_item(item, spider)
                except DropItem:
                    # do not further process the item
                    pass

    async def close(self):
        await self.crawler.close()

    def _load_pipeline(self, pipeline_class, crawler):
        if hasattr(pipeline_class, 'from_crawler'):
            return pipeline_class.from_crawler(crawler)
        else:
            return pipeline_class()


class Semaphore(object):
    def __init__(self, conn, namespace, spider):
        self.conn = conn
        self.namespace = namespace
        self.spider = spider
        self.timeout_minutes = 60

    def acquire(self):
        c = self.conn.cursor()
        c.execute('''UPDATE skyscraper_spiders
            SET blocked_from_running_until = NOW() at time zone 'utc'
                + INTERVAL '%s minutes'
            -- fail if somebody else blocked it
            WHERE (
                blocked_from_running_until IS NULL
                OR blocked_from_running_until < NOW() at time zone 'utc'
            )
            AND name = %s
            AND project_id IN (
                SELECT project_id FROM projects WHERE name = %s
            )''',
            (self.timeout_minutes, self.spider, self.namespace))
        self.conn.commit()

        if c.rowcount == 0:
            raise Exception('Could not acquire lock')

    def locked(self):
        c = self.conn.cursor()
        c.execute('''SELECT COUNT(*) FROM skyscraper_spiders s
            JOIN projects p ON s.project_id = p.project_id
            WHERE blocked_from_running_until >= NOW() at time zone 'utc'
            AND s.name = %s
            AND p.name = %s''', (self.spider, self.namespace))
        row = c.fetchone()
        return row is not None

    def release(self):
        c = self.conn.cursor()
        c.execute('''UPDATE skyscraper_spiders
            SET blocked_from_running_until = NULL
            WHERE name = %s
            AND project_id IN (
                SELECT project_id FROM projects WHERE name = %s
            )''', (self.spider, self.namespace))
        self.conn.commit()
