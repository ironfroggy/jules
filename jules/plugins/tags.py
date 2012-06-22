import os

import jules


def preprocess_bundle(k, bundle, engine):
    if 'tags' in bundle.meta:
        bundle.tags = bundle.meta['tags']
    else:
        bundle.tags = []

    tags = engine.context.setdefault('tags', {})
    tag_bundles = {}
    for tag in bundle.tags:
        if tag not in tags:
            key = 'tags/{tag}'.format(tag=tag)
            tag_bundle = tag_bundles[key] = jules.Bundle(key)
            tag_bundle.meta.update({
                'tag': tag,
                'template': 'tag.j2',
                'render': 'jinja2',
            })
            tag_bundle.meta.setdefault('bundles', set()).add(bundle)
            
        tags.setdefault(tag, set()).add(bundle.key)
    if tag_bundles:
        engine.add_bundles(tag_bundles)


def find_bundles():
    tag_bundle = jules.BundleFactory('tags/{tag}')
    return [tag_bundle]
