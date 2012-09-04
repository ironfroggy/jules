import os

import jules


class TagBundle(jules.Bundle):

    def __init__(self, key, tagname):
        super(TagBundle, self).__init__(key)
        self.tagname = tagname
        self.tagged = set()
        self.meta.update({
            'template': 'tag.j2',
            'render': 'jinja2',
        })

    def render(self, engine, output_dir):
        """Tags have a side-effect of rendering a tag-specific feed."""

        super(TagBundle, self).render(engine, output_dir)
        self._render_with(engine, output_dir,
            engine.get_template("atom.j2"),
            "tags/{}.xml".format(self.tagname),
            )

    def _url(self):
        return "/{}/".format(self.key.strip('/'))

    def get_bundles_by(self, *args, **kwargs):
        return jules.utils.filter_bundles(self.tagged, *args, **kwargs)


def find_bundles():
    tag_bundle = jules.BundleFactory('tags/{tag}')
    return [tag_bundle]


def preprocess_bundle(k, bundle, engine):
    tags = engine.context.setdefault('tags', {})
    if bundle.meta.get('status') != 'published':
        return
    if 'tags' in bundle.meta:
        bundle.tags = bundle.meta['tags']
    else:
        bundle.tags = []

    tag_bundles = {}
    for tag in bundle.tags:
        if tag not in tags:
            key = engine.config.get('tag_path', '{tag}/').format(tag=tag)
            tag_bundle = TagBundle(key, tag)
            tag_bundles[tag] = tag_bundle
            tags[tag] = tag_bundle
        else:
            tag_bundle = tags[tag]
        tag_bundle.tagged.add(bundle)
    if tag_bundles:
        engine.add_bundles(tag_bundles)
