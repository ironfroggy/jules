import os

import jules


def preprocess_bundle(k, bundle, engine):
    if 'tags' in bundle.meta:
        bundle.tags = bundle.meta['tags']
    else:
        bundle.tags = []

    tags = engine.context.setdefault('tags', {})
    for tag in bundle.tags:
        tags.setdefault(tag, set()).add(bundle.key)


def find_bundles():
    tag_bundle = jules.BundleFactory('tags/{tag}')
    return [tag_bundle]
