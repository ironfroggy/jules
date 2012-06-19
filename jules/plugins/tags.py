import os


def preprocess_bundle(k, bundle, engine):
    if 'tags' in bundle.meta:
        bundle.tags = bundle.meta['tags']
    else:
        bundle.tags = []
