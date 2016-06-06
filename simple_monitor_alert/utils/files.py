import json
import os
import sys


if sys.version_info < (3, 2):
    def makedirs(path, mode=0o777, exist_ok=False):
        if not exist_ok or (exist_ok and not os.path.exists(path)):
            os.makedirs(path, mode)
else:
    from os import makedirs


def validate_write_dir(directory, log=lambda x: x):
    if os.path.lexists(directory) and os.access(directory, os.W_OK):
        return True
    if os.path.lexists(directory) and not os.path.exists(directory):
        log('{} exists but the destination does not exist. Is a broken link?'.format(directory))
        return False
    try:
        makedirs(directory, exist_ok=True)
    except OSError:
        log('No write permissions to the directory {}.'.format(directory))
        return False
    return os.access(directory, os.W_OK)


def create_file(path, content=''):
    import six
    if not isinstance(content, six.string_types):
        content = json.dumps(content)
    if not os.path.exists(path):
        with open(path, 'w') as f:
            f.write(content)
    return path


class JSONFile(dict):
    def __init__(self, path, create=True):
        super(JSONFile, self).__init__()
        if create:
            create_file(path, '{}')
        self.path = path
        self.read()

    def read(self):
        self.clear()
        self.update(json.load(open(self.path)))

    def write(self):
        json.dump(self, open(self.path, 'w'), sort_keys=True, indent=4, separators=(',', ': '))

    def clear(self):
        if sys.version_info >= (3, 3):
            super().clear()
        else:
            for key in self:
                del self[key]