import os

import jules


class TagBundle(jules.Bundle):

    def __init__(self, tagname):
        super(TagBundle, self).__init__('tags/' + tagname)
        self.tagname = tagname
        self.tagged = set()
        self.meta.update({
            'template': 'tag.j2',
            'render': 'jinja2',
        })


def preprocess_bundle(k, bundle, engine):
    if 'tags' in bundle.meta:
        bundle.tags = bundle.meta['tags']
    else:
        bundle.tags = []

    tags = engine.context.setdefault('tags', {})
    tag_bundles = {}
    for tag in bundle.tags:
        if tag not in tags:
            tag_bundle = TagBundle(tag)
            tag_bundles[tag_bundle.key] = tag_bundle
            tag_bundle.tagged.add(bundle)
            
        tags.setdefault(tag, set()).add(bundle.key)
    if tag_bundles:
        engine.add_bundles(tag_bundles)


def find_bundles():
    tag_bundle = jules.BundleFactory('tags/{tag}')
    return [tag_bundle]
