from __future__ import print_function


import os

import yaml

from jules.utils import maybe_call, middleware


plugin_order = -100


def preprocess_bundle(bundle_key, bundle, engine):
    meta = bundle.setdefault('meta', {})
    yaml_filename = bundle.by_ext('yaml')
    if yaml_filename:
        data = yaml.load(open(yaml_filename))
        if data is not None:
            meta.update(data)
