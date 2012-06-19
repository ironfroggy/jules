from __future__ import print_function


import re
import os

import yaml

from jules.utils import maybe_call, middleware


plugin_order = -100


def preprocess_input_dirs(input_dirs):
    def key(filename):
        d = re.search(r'^(\d+)', filename)
        if d:
            d = int(d.groups()[0])

        s = re.search(r'^\d?([^\d]+)', filename)
        if s:
            s = s.groups()[0]

        return (d, s)
    input_dirs.sort(key=key)


def prepare_input_dir(input_dir):
    pass

def preprocess_bundle(bundle_key, bundle, engine):
    meta = bundle.setdefault('meta', {})
    yaml_filename = bundle.by_ext('yaml')
    if yaml_filename:
        data = yaml.load(open(yaml_filename))
        if data is not None:
            meta.update(data)
