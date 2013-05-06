from __future__ import print_function
from jules.filters import register


import os

import yaml


plugin_order = -100


@register
def sortbundles(bundles, props):
    bundles = list(bundles)
    props = props.split(',')
    def key(bundle):
        values = []
        for prop in props:
            value = bundle.meta.get(prop, 0)
            if hasattr(value, 'lower'):
                value = value.lower()
            values.append(value)
        return tuple(values)
    bundles.sort(key=key)
    return bundles

