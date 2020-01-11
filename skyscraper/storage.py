import json
import os
import uuid


from .items import Item, DownloadItem


class JsonStorage(object):
    def __init__(self, items_folder, downloads_folder):
        self.items_folder = items_folder
        self.downloads_folder = downloads_folder

    def store_item(self, item):
        project = item.namespace
        spider = item.spider
        random_id = str(uuid.uuid4())

        if isinstance(item, Item):
            filename = '{}.json'.format(random_id)
            destination_folder = os.path.join(self.items_folder, project, spider)
            os.makedirs(destination_folder, exist_ok=True)
            filepath = os.path.join(destination_folder, filename)

            with open(filepath, 'w+') as f:
                f.write(json.dumps(item))

        elif isinstance(item, DownloadItem):
            if item.extension:
                filename = '{}.{}'.format(random_id, item.extension)
            else:
                filename = random_id

            destination_folder = os.path.join(self.downloads_folder, project, spider)
            os.makedirs(destination_folder, exist_ok=True)
            filepath = os.path.join(destination_folder, filename)

            with open(filepath, 'wb+') as f:
                f.write(item.bytes)
