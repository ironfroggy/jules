"""

Example Configuration:

collections:
    tags:
        match:
            status: published
        group_by:
            - property: tags
              rule: in
    series:
        match:
            status: published
        order: publish_time
        group_by:
            - property: series
              rule: equals
"""

import jules


class Collection(jules.Bundle):
    """Each collection represents one group of bundles, grouped by a given
    property they share a value with one another on. For example, if they
    all share at least one tag, or if they are in the same series.
    """

    def __init__(self, key, rule, group_by_property, value, meta):
        super(Collection, self).__init__(key)
        self.active = False
        self.rule = rule
        self.group_by_property = group_by_property
        self.value = value
        self._meta = meta

        self.bundles = set()

    def render(self, engine, output_dir):
        """Collections have the side-effect of rendering a
        collection-specific feed.
        """

        r = super(Collection, self).render(engine, output_dir)
        self._render_with(engine, output_dir,
            engine.get_template("atom.j2"),
            "feeds/{}/atom.xml".format(self.value),
            )
        return r

    def get_bundles_by(self, *args, **kwargs):
        return jules.utils.filter_bundles(self.bundles, *args, **kwargs)

    def add_bundle(self, bundle):
        if bundle.meta['status'] == 'published':
            self.active = True
        self.bundles.add(bundle)


class Collector(object):
    def __init__(self, engine, name, match, group_by, order='slug'):
        self.engine = engine
        self.name = name
        self.match = match
        self.group_by = group_by
        self.order = order

        self.collections = {}

        # Load shared config for collections
        self.meta = engine.config['collections'][name].get('meta', {})

    def collect(self, rule, group_by_property, bundle):
        """Collect the bungle if it is a proper candidate for the collection.

        rule: The rule to match the bundle by.
            is - match if the grouper property is equal to the group value
            in - match if the grouper property contains the group value
        group_by_property: The meta property on which to group bundles by
        bundle: The bundle to collect, if it matches the rules, into one
            of the collections being kept by theis collector.
        """

        try:
            value = bundle.meta[group_by_property]
        except KeyError:
            pass
        else:
            if rule == 'is':
                values = [value]
            elif rule == 'in':
                values = value

            for value in values:
                key = '%s/%s' % (group_by_property, value)
                if not value in self.collections:
                    collection = Collection(key, rule, group_by_property, value, self.meta)
                    self.engine.add_bundles({
                        key: collection,
                    })
                    self.collections[value] = collection
                    collection[bundle.key] = bundle
            # All bundles need a copy of this collection
            for colkey, collection in self.collections.items():
                for value in values:
                    self.engine.context['collections'].setdefault(group_by_property, set()).add(collection)
                    if value == collection.value:
                        bundle.meta['collections'].setdefault(group_by_property, set()).add(collection)
                        collection.add_bundle(bundle)


def preprocess_bundle(k, bundle, engine):
    """Find all collections this bundle is a member of."""

    # Shared set of collectors and resulting collections
    collectors = engine.context.setdefault('collectors', {})
    collections = engine.context.setdefault('collections', {})
    # Collections this bundle is a member of
    bundle.meta.setdefault('collections', {})

    for name, collector in engine.config.get('collections', {}).items():
        match = collector.get('match')
        group_by = collector['group_by']
        order = collector.get('order', 'slug')
        collectors.setdefault(name, Collector(engine, name,
            match=match,
            group_by=group_by,
            order=order,
        ))

        for group_rule, group_property in collector['group_by'].items():
            collectors[name].collect(group_rule, group_property, bundle)
    for n, collector in collectors.items():
        collections.update(collector.collections)
        for n, collection in collector.collections.items():
            collection.prepare(engine)

