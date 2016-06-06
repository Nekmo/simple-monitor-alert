import os
import sys

if sys.version_info < (3, 2):
    def makedirs(path, mode=0o777, exist_ok=False):
        if not exist_ok or (exist_ok and not os.path.exists(path)):
            os.makedirs(path, mode)
else:
    from os import makedirs
