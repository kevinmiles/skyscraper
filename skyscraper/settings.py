# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(usecwd=True))


BOT_NAME = 'skyscraper'

SPIDER_MODULES = ['skyscraper.spiders']
NEWSPIDER_MODULE = 'skyscraper.spiders'

if os.environ.get('SKYSCRAPER_LOGLEVEL'):
    LOG_LEVEL = os.environ.get('SKYSCRAPER_LOGLEVEL')
else:
    LOG_LEVEL = 'DEBUG'

if os.environ.get('SKYSCRAPER_USER_AGENT'):
    USER_AGENT = os.environ.get('SKYSCRAPER_USER_AGENT')
else:
    USER_AGENT = 'Mozilla/5.0 (compatible; Molescrape Skyscraper; ' \
                 + '+http://www.molescrape.com/)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DOWNLOAD_DELAY = float(os.environ.get('SKYSCRAPER_DOWNLOAD_DELAY', 1))


ITEM_PIPELINES = {
    'skyscraper.pipelines.metainfo.AddNamespacePipeline': 100,
    'skyscraper.pipelines.metainfo.AddSpiderNamePipeline': 101,
    'skyscraper.pipelines.metainfo.AddCrawlTimePipeline': 102,
}

if os.environ.get('SKYSCRAPER_PIPELINE_USE_DUPLICATESFILTER_DISK') \
        and int(os.environ.get('SKYSCRAPER_PIPELINE_USE_DUPLICATESFILTER_DISK')):
    ITEM_PIPELINES['skyscraper.pipelines.filesystem.DiskDeduplicationPipeline'] = 200

    DISK_DEDUPLICATION_FOLDER = os.environ.get('SKYSCRAPER_DISK_DEDUPLICATION_FOLDER')

if os.environ.get('SKYSCRAPER_PIPELINE_USE_DUPLICATESFILTER_DYNAMODB') \
        and int(os.environ.get('SKYSCRAPER_PIPELINE_USE_DUPLICATESFILTER_DYNAMODB')):
    ITEM_PIPELINES['skyscraper.pipelines.aws.DoNotStoreDuplicatesPipeline'] = 200

    # should be immediately after SaveDataPipeline
    ITEM_PIPELINES['skyscraper.pipelines.aws.StoreItemToDuplicateFilterPipeline'] = 301

if os.environ.get('SKYSCRAPER_PIPELINE_USE_OUTPUT_FOLDER') \
        and int(os.environ.get('SKYSCRAPER_PIPELINE_USE_OUTPUT_FOLDER')):
    ITEM_PIPELINES['skyscraper.pipelines.filesystem.SaveDataToFolderPipeline'] = 300

# These variables must always be set, not only when SKYSCRAPER_PIPELINE_USE_OUTPUT_FOLDER
# is active. The PIPELINE setting enabled the Scrapy pipeline, but the
# storage paths are also used for non-scrapy spiders
local_storage = os.path.join(os.getcwd(), 'results')
SKYSCRAPER_STORAGE_FOLDER_PATH = os.environ.get(
    'SKYSCRAPER_STORAGE_FOLDER_PATH',
    default=local_storage)
SKYSCRAPER_STORAGE_DOWNLOADS_PATH = os.environ.get(
    'SKYSCRAPER_STORAGE_DOWNLOADS_PATH',
    default=local_storage)

if os.environ.get('SKYSCRAPER_CHROME_NO_SANDBOX'):
    SKYSCRAPER_CHROME_NO_SANDBOX = bool(os.environ.get('SKYSCRAPER_CHROME_NO_SANDBOX'))
else:
    SKYSCRAPER_CHROME_NO_SANDBOX = False

if os.environ.get('SKYSCRAPER_PROMETHEUS_METRICS_PORT'):
    PROMETHEUS_METRICS_PORT = int(os.environ.get('SKYSCRAPER_PROMETHEUS_METRICS_PORT'))
else:
    PROMETHEUS_METRICS_PORT = None

# Connection to AWS
AWS_ACCESS_KEY = os.environ.get('SKYSCRAPER_AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('SKYSCRAPER_AWS_SECRET_ACCESS_KEY')

DYNAMODB_CRAWLING_INDEX = os.environ.get('SKYSCRAPER_DYNAMODB_CRAWLING_INDEX')
DYNAMODB_CRAWLING_OPTIONS = os.environ.get('SKYSCRAPER_DYNAMODB_CRAWLING_OPTIONS')

# Spider management
GIT_REPOSITORY = os.environ.get('SKYSCRAPER_GIT_REPOSITORY')
GIT_WORKDIR = os.environ.get('SKYSCRAPER_GIT_WORKDIR')
GIT_SUBFOLDER = os.environ.get('SKYSCRAPER_GIT_SUBFOLDER')
GIT_BRANCH = os.environ.get('SKYSCRAPER_GIT_BRANCH')

SPIDER_LOADER_CLASS = 'skyscraper.spiderloader.FolderSpiderLoader'
# Fixed spider folder, e.g. for testing
# In daemon mode this will be set to the git directory
if os.environ.get('SKYSCRAPER_SPIDERS_FOLDER'):
    SPIDERS_FOLDER = os.environ.get('SKYSCRAPER_SPIDERS_FOLDER')
else:
    SPIDERS_FOLDER = GIT_WORKDIR
