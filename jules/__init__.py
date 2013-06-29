from __future__ import print_function


import os
import re
import shutil
from fnmatch import fnmatch

import yaml
from straight.plugin import load

import jules
import jules.filters, jules.query, jules.plugins


PACKAGE_DIR = os.path.dirname(__file__)

class JulesEngine(object):
    def __init__(self, src_path):
        self.src_path = src_path
        self.config = self._load_config()
        self.input_dirs = self._find_input_dirs()
        self.plugins = PluginDB(self)
        self.bundles = self.load_bundles()
        
        # try to defer circular dependencies until JulesEngine is as initialized
        # as possible. Here, plugins are passed partially-initialized
        # instances of JulesEngine. (BLEH.)
        self.prepare_bundles()
        self.engine_plugins = list(self.plugins.produce_instances(
            jules.plugins.EnginePlugin))
        self.query_engine = jules.query.QueryEngine(self)
    
    def _load_config(self):
        config_path = os.path.join(self.src_path, 'site.yaml')
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f)
        else:
            raise ValueError(
                "No configuration file found. Looking for site.yaml at `{}`."
                .format(self.src_path))
        
        config.setdefault(
            'templates',
            [os.path.join(self.src_path, 'templates')])
        config.setdefault('entries', [])
        config['output_dir'] = os.path.join(
            self.src_path,
            config.get('output_dir', '_build'))
        
        return config

    def _find_input_dirs(self):
        input_dirs = []

        for bundle_dir in self.config.get('bundle_dirs', ()):
            input_dirs.append(
                os.path.abspath(os.path.join(self.src_path, bundle_dir)))

        def key(filename):
            d = re.search(r'^(\d+)', filename)
            if d:
                d = int(d.groups()[0])

            s = re.search(r'^\d?([^\d]+)', filename)
            if s:
                s = s.groups()[0]

            return (d, s)
        input_dirs.sort(key=key)

        return input_dirs


    def load_bundles(self):
        """Load a site by loading configuration, plugins, packs, and bundles."""

        bundles = {}
        for loaded_bundles in self.plugins.middleware('find_bundles', loader=self):
            for bundle in loaded_bundles:
                bundles[bundle.key] = bundle

        return bundles
    
    def prepare_bundles(self):
        for k, bundle in self.bundles.iteritems():
            bundle.prepare(self)
    
    def run(self):
        self.initialize()
        self.render_all()
        self.finalize()
    
    def initialize(self):
        for plugin in self.engine_plugins:
            plugin.initialize()
    
    def finalize(self):
        for plugin in self.engine_plugins:
            plugin.finalize()
        
    def render_all(self):
        """Render queries in `entries` section of config"""
        for q in self.config['entries']:
            (query_name, pipeline), = q.iteritems()
            self._render_query(query_name, pipeline)
    
    def _render_query(self, name, pipeline):
        results = self.bundles.values()
        for stmt in pipeline:
            (dispatch_key, arg), = stmt.iteritems()
            results = self.query_engine.dispatch(dispatch_key, results, arg)
        list(results)


# TODO: this class seems a little like poor organization
class PluginDB(object):
    def __init__(self, engine, default_ns='jules.plugins'):
        self.plugins = load(default_ns)
        self.plugins._plugins.sort(key=lambda p: getattr(p, 'plugin_order', 0))
        self.instance_cache = {}
        self.ns = default_ns
        self.engine = engine

    def middleware(self, method, *args, **kwargs):
        """Call each loaded plugin with the same method, if it exists."""

        kwargs['engine'] = self.engine
        return list(self.plugins.call(method, *args, **kwargs))
    
    def first(self, method, *args, **kwargs):
        kwargs['engine'] = self.engine
        return self.plugins.first(method, *args, **kwargs)

    def pipeline(self, method, first, *args, **kwargs):
        """Call each loaded plugin with the same method, if it exists,
        passing the return value of each as the first argument of the
        next.
        """

        kwargs['engine'] = self.engine
        return self.plugins.pipe(method, first, *args, **kwargs)
    
    def load(self, *args, **kwargs):
        return load(kwargs.pop('ns', self.ns), *args, **kwargs)
    
    def produce_instances(self, base_cls, ns=None):
        """Yield instances of a plugin type, caching them.
        
        A class will only be instantiated once if retrieved using
        produce_instances, even if produce_instances retrieves it many times,
        even for different base classes / base plugin types.
        
        Useful because sometimes a plugin may be a plugin of multiple types,
        but only one instance should exist for a single JulesEngine. This way
        a single plugin can have shared state across multiple parts of the
        production process.
        """
        if ns is None:
            ns = self.ns
        for Plugin in self.load(subclasses=base_cls, ns=ns):
            yield self.produce_instance(Plugin)
    
    def produce_instance(self, cls, *args, **kwargs):
        try:
            return self.instance_cache[cls]
        except KeyError:
            # FIXME: check for recursion using something like
            #        self.instance_recurse_cache.
            #        (we mutually recurse with produce_new_instance)
            return self.instance_cache.setdefault(
                cls,
                self.produce_new_instance(cls, *args, **kwargs))
    
    def produce_new_instance(self, cls, *args, **kwargs):
        # FIXME: recurse through base classes for deps
        deps = map(self.produce_instance, cls.dependencies)
        # FIXME: make engine just another dependency
        args = args + (self.engine,) + tuple(deps)
        return cls(*args, **kwargs)

class _BundleMeta(object):
    """This is a dict-like object for bundle meta data."""

    def __init__(self, defaults, meta):
        self.defaults = defaults
        self.meta = meta
    def __contains__(self, key):
        return key in self.meta or key in self.defaults
    def __getitem__(self, key):
        try:
            return self.meta[key]
        except KeyError:
            return self.defaults[key]
    def __setitem__(self, key, value):
        self.meta[key] = value
    def __delitem__(self, key):
        del self.meta[key]
    def __iter__(self):
        return iter(self.meta)
    def keys(self):
        return self.meta.keys()
    def get(self, key, default=None):
        try:
            value = self.meta[key]
        except KeyError:
            try:
                value = self.defaults[key]
            except KeyError:
                value = default
        return value
    def setdefault(self, key, default=None):
        try:
            value = self.meta[key]
        except KeyError:
            try:
                value = self.defaults[key]
            except KeyError:
                self.meta[key] = default
                value = default
        return value
    def update(self, data):
        self.meta.update(data)

class BundleConflict(Exception): pass

class Bundle(object):
    """Each bundle is a collection of input files, properties, and meta data."""

    def __init__(self, key, directory, path, defaults=None):
        self.key = key
        self.directory = directory
        self.path = path
        self._metadefaults = defaults or {}
        self.components = {}
        self.meta = None

    def __str__(self):
        return 'Bundle(key=%r)' % (self.key,)

    @property
    def recent(self):
        """The updated, published, or created time. The first to exist is given."""

        M = self.meta
        return M['updated_time'] or M['publish_time'] or M['created_time']

    def prepare(self, engine):
        """Prepare the bundle for querying and rendering."""
        self._load_components(engine)
        self._postprocess_compononents()
    
    def _load_components(self, engine):
        # FIXME: allow components to be placed in other directories via some
        # kind of mechanism. unsure how to proceed. For now, tossing this
        # feature of original system.
        component_plugins = engine.plugins.load(
            subclasses=jules.plugins.ComponentPlugin)
        occupied_basenames = {}
        # FIXME: occupy meta fields as well?
        # FIXME: occupy config fields as well?
        # FIXME: allow components to depend on other components.
        # FIXME: URGENT: allow components to depend on plugins
        
        for plugin in component_plugins:
            for basename in plugin.basenames:
                if basename in occupied_basenames:
                    other = occupied_basenames[basename]
                    all_conflicts = ', '.join(
                        sorted(set(other.basenames) & set(plugin.basenames)))
                    raise BundleConflict(
                        "{p1} and {p2} conflict over these basenames: {bases}"
                        .format(
                            bases = all_conflicts,
                            p1 = other.__name__,
                            p2 = plugin.__name__))
            # no conflict
            occupied_basenames.update(dict.fromkeys(plugin.basenames, plugin))
        
        plugin_loads = {}
        for sub in os.listdir(self.path):
            basename, ext = os.path.splitext(sub)
            subpath = os.path.join(self.path, sub)
            try:
                plugin = occupied_basenames[basename]
            except KeyError:
                # FIXME: warn about unused file?
                continue
            paths = plugin_loads.setdefault(plugin, {})
            paths[basename] = (ext, subpath)
        
        for plugin_cls, paths in plugin_loads.iteritems():
            plugin = plugin_cls(engine)
            component = plugin.maybe_load(**{base:paths[base]
                for base in plugin.basenames})
            if component is not None:
                self.components[plugin.name] = component

    def _postprocess_compononents(self):
        self.components['meta']['key'] = self.key
        self.components['meta']['directory'] = self.directory
        self.meta = _BundleMeta(self._metadefaults, self.components['meta'])

