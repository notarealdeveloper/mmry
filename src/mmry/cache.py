__all__ = [
    'Cache',
    'CacheSha1',
]

import os
import assure
import hashlib
from functools import lru_cache

class CacheSha1:

    """ Content addressable memory, inspired by git. """

    @staticmethod
    def default_root():
        return os.path.join(os.getenv('HOME'), '.cache', 'mmry')

    @staticmethod
    def default_name():
        return 'global'

    def __init__(self, name=None, *, root=None):
        self.root = root or self.default_root()
        self.name = name or self.default_name()

    def namespace(self, name=None):
        if name: self.name = name
        else:    return self.name        

    @property
    def blobs(self):
        return os.path.join(self.root, self.name, 'blobs')

    @property
    def trees(self):
        return os.path.join(self.root, self.name, 'trees')

    def have(self, blob):
        return os.path.exists(self.path(blob))

    def path(self, blob):
        return os.path.join(self.blobs, self.hash(blob))

    def check_name(self, name):
        if '/' in name:
            raise ValueError(f"name cannot contain '/'")

    def have_name(self, name):
        self.check_name(name)
        dst = self.full_name(name)
        return os.path.exists(dst)

    def full_name(self, name):
        return os.path.join(self.trees, name)

    def save_name(self, name, blob):
        self.check_name(name)
        dst = self.full_name(name)
        src = self.path(blob)
        os.symlink(src, dst)

    def load_name(self, name) -> bytes:
        self.check_name(name)
        path = self.full_name(name)
        return self.load_path(path)

    def delete_name(self, name):
        self.check_name(name)
        path = self.full_name(name)
        return self.delete_path(name)

    def save(self, blob, bytes):
        path = self.path(blob)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as fp:
            fp.write(assure.bytes(bytes))

    def load(self, blob) -> bytes:
        path = self.path(blob)
        return self.load_path(path)

    def load_path(self, path):
        with open(path, 'rb') as fp:
            return assure.bytes(fp.read())

    def delete(self, blob):
        path = self.path(blob)
        return self.delete_path(path)

    def delete_path(self, path):
        try:
            os.remove(path)
        except:
            return False
        else:
            return True

    def hash(self, blob):
        return self.hash_bytes(self.ensure_bytes(blob))

    @staticmethod
    @lru_cache
    def ensure_bytes(blob):
        return blob.encode() if isinstance(blob, str) else blob

    @staticmethod
    @lru_cache
    def hash_bytes(blob):
        """ ensure we only cache content once, even if it arrives in
            one call as a unicode string, and in a later call as bytes.
        """
        if not isinstance(blob, bytes):
            raise TypeError(f"blob has type {blob.__class__.__name__!r}")
        return hashlib.sha1(blob).hexdigest()

# Default
Cache = CacheSha1
