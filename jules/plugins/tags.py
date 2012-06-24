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

    def url(self):
        return "/tags/{}.html".format(self.tagname)

    def get_bundles_by(self, *args, **kwargs):
        return jules.utils.filter_bundles(self.tagged, *args, **kwargs)


def preprocess_bundle(k, bundle, engine):
    if bundle.meta.get('status') != 'published':
        return
    if 'tags' in bundle.meta:
        bundle.tags = bundle.meta['tags']
    else:
        bundle.tags = []

    tags = engine.context.setdefault('tags', {})
    tag_bundles = {}
    for tag in bundle.tags:
        if tag not in tags:
            tag_bundle = TagBundle(tag)
            tag_bundles[tag] = tag_bundle
            tags[tag] = tag_bundle
        else:
            tag_bundle = tags[tag]
        tag_bundle.tagged.add(bundle)
    if tag_bundles:
        engine.add_bundles(tag_bundles)


def find_bundles():
    tag_bundle = jules.BundleFactory('tags/{tag}')
    return [tag_bundle]
