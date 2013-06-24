import os
from datetime import date, datetime

from straight.plugin import load


def ensure_path(path):
    path_parts = os.path.split(path)
    for i in range(len(path_parts)):
        subpath = os.path.join(*path_parts[: i + 1 ])
        if subpath and not os.path.exists(subpath):
            os.mkdir(subpath)