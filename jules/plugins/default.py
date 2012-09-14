from __future__ import print_function
from jules.filters import register


import os

import yaml


plugin_order = -100


@register
def sortbundles(bundles, prop):
    bundles = list(bundles)
    def key(bundle):
        value = bundle.meta[prop]
        if hasattr(value, 'lower'):
            return value.lower()
        else:
            return value
    bundles.sort(key=key)
    return bundles

