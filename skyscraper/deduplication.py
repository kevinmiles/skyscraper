# Based on analysis from running several spiders (~20) for a bit more than
# one year we saw that we have around the following numbers:
# - 8.5 million different unique IDs
# - 2.5 GB in total
# - strings might have a very long common prefix

import os
import hashlib


class DiskTrieDuplicatesFilter(object):
    # TODO: This is the simplest approach possible.
    # Check where this performs well and where we have to
    # change things and then adjust
    def __init__(self, trie_directory):
        self.trie_directory = trie_directory

    def add_word(self, word):
        bucket = self._determine_bucket(word)

        bucketfile = os.path.join(self.trie_directory, bucket)
        with open(bucketfile, 'a+') as f:
            f.write('{}\n'.format(word))

    def has_word(self, word):
        bucket = self._determine_bucket(word)

        bucketfile = os.path.join(self.trie_directory, bucket)
        if not os.path.isfile(bucketfile):
            return False

        with open(bucketfile, 'r') as f:
            for line in f:
                if line.strip() == word:
                    return True

        return False

    def _determine_bucket(self, word):
        # use the first two chars of the hash. This should produce a quite
        # good distribution for our 2.5 GB (see above)
        h = hashlib.sha256(word.encode('utf-8'))
        digest = h.hexdigest()
        return digest[0:2]
