import json
import os
import uuid


class JsonStorage(object):
    def __init__(self, target_folder):
        self.target_folder = target_folder

    def store_item(self, item):
        project = item['namespace']
        spider = item['spider']
        random_id = str(uuid.uuid4())
        filename = '{}.json'.format(random_id)

        destination_folder = os.path.join(self.target_folder, project, spider)

        try:
            os.makedirs(destination_folder)
        except OSError:
            # Already exists
            pass

        filepath = os.path.join(destination_folder, filename)
        with open(filepath, 'w+') as f:
            f.write(json.dumps(item))
