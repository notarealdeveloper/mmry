__all__ = [
    'Cache',
]

import os
import assure
import hashlib
from functools import lru_cache


class Cache:

    """ Content addressable memory, inspired by git. """

    @staticmethod
    def default_root():
        # prioritize environment variable if user has set it
        if (root := os.getenv('MMRY_CACHE_ROOT')):
            return root
        # otherwise, use the canonical location in $HOME
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
    def path(self):
        return os.path.join(self.root, self.name)

    @property
    def blobs(self):
        return os.path.join(self.path, 'blobs')

    @property
    def names(self):
        return os.path.join(self.path, 'names')

    def rmtree(self, confirm=False):
        self.check_path(self.root)
        self.check_path(self.path)
        if confirm:
            import shutil
            try:    shutil.rmtree(self.path)
            except: pass
        else:
            print(f"skipping: shutil.rmtree({self.path})")

    #############
    ### paths ###
    #############

    def save_path(self, path, bytes):
        with umask():
            os.makedirs(os.path.dirname(path), mode=MODE, exist_ok=True)
            with open(path, 'wb') as fp:
                return fp.write(assure.bytes(bytes))

    def load_path(self, path):
        with open(path, 'rb') as fp:
            return assure.bytes(fp.read())

    def delete_path(self, path):
        try:    os.remove(path)
        except: return False
        else:   return True

    def have_path(self, path):
        return os.path.exists(path)

    def check_path(self, path):
        if not path.startswith(self.root):
            raise ValueError(f"Bad path: {path}")
        return True

    #############
    ### blobs ###
    #############

    def blob_path(self, blob):
        path = os.path.join(self.blobs, self.hash(blob))
        self.check_path(path)
        return path

    def have_blob(self, blob):
        path = self.blob_path(blob)
        return self.have_path(path)

    def save_blob(self, blob, bytes):
        path = self.blob_path(blob)
        return self.save_path(path, bytes)

    def load_blob(self, blob) -> bytes:
        path = self.blob_path(blob)
        return self.load_path(path)

    def delete_blob(self, blob):
        path = self.blob_path(blob)
        return self.delete_path(path)

    #############
    ### names ###
    #############

    def check_name(self, name):
        if '/' in name:
            raise ValueError(f"name cannot contain '/'")
        return name

    def name_path(self, name):
        path = os.path.join(self.names, name)
        self.check_name(name)
        return path

    def have_name(self, name):
        path = self.name_path(name)
        return self.have_path(path)

    def save_name(self, name, blob):
        with umask():
            os.makedirs(self.names, mode=MODE, exist_ok=True)
        src = self.name_path(name)
        dst = self.blob_path(blob)
        if self.have_path(src):
            # assert dst == os.readlink(src)
            self.delete_name(name)
        os.symlink(dst, src)

    def load_name(self, name) -> bytes:
        path = self.name_path(name)
        return self.load_path(path)

    def delete_name(self, name):
        path = self.name_path(name)
        return self.delete_path(path)

    #################
    ### internals ###
    #################

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


# group writeable, but not world
MASK = 0o002
MODE = 0o775

class umask:
    def __init__(self, mask=MASK):
        self.new = mask
    def __enter__(self):
        self.old = os.umask(self.new)
    def __exit__(self, *args):
        os.umask(self.old)
