from __future__ import print_function

from collections import defaultdict
import os
import re
import shutil
from fnmatch import fnmatch
import warnings

import yaml
from straight.plugin import load
import jinja2

import jules
import jules.filters
import jules.plugins.default
from jules.utils import ensure_path, filter_bundles


PACKAGE_DIR = os.path.dirname(__file__)


class JulesEngine(object):

    def __init__(self, src_path):
        self.src_path = src_path
        self.input_dirs = [os.path.join(PACKAGE_DIR, 'packs', 'jules')]
        self.bundles = {}
        self._new_bundles = {}
        self.context = {}
        self.config = defaultdict(lambda: None)
        self.plugins = []

    def load_config(self):
        """Populates engine.config with the site configuration."""

        config_path = os.path.join(self.src_path, 'site.yaml')
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config.update(yaml.safe_load(f))
        else:
            raise ValueError("No configuration file found. Looking for site.yaml at `{}`.".format(self.src_path))

    def prepare(self):
        """Prepare a site by loading configuration, plugins, packs, and bundles."""

        self.load_config()
        self.load_plugins()
        for ns in self.config.get('plugins', ()):
            self.load_plugins(ns)

        for pack_def in self.config.get('packs', ()):
            pack_type, pack_name = pack_def.split(':', 1)
            if pack_type == 'jules':
                self.input_dirs.append(os.path.join(PACKAGE_DIR, 'packs', pack_name))
            elif pack_type == 'dir':
                self.input_dirs.append(os.path.abspath(pack_name))

        self._jinja_env = jinja2.Environment(
            loader = jinja2.loaders.FileSystemLoader(self.input_dirs),
        )
        for filter_name in dir(jules.filters):
            if not filter_name.startswith('_'):
                self._jinja_env.filters[filter_name] = getattr(jules.filters, filter_name)
                print('load filter', filter_name)

        def key(filename):
            d = re.search(r'^(\d+)', filename)
            if d:
                d = int(d.groups()[0])

            s = re.search(r'^\d?([^\d]+)', filename)
            if s:
                s = s.groups()[0]

            return (d, s)
        self.input_dirs.sort(key=key)

        self.find_bundles()
    
    def reload_source(self, path=None):
        # Todo: add cache for unchanged contents
        for key, bundle in self.bundles.items():
            reload_bundle = False
            if path is None:
                reload_bundle = True
            else:
                path = os.path.abspath(path)
                for entry in bundle.entries:
                    entry_path = os.path.abspath(os.path.join(*entry))
                    if path == entry_path:
                        reload_bundle = True
            if reload_bundle:
                bundle._meta = None
                bundle.content = None
        self.prepare_bundles()

    def find_bundles(self):
        """Find all bundles in the input directories, load them, and prepare them."""

        defaults = self.config.get('bundle_defaults', {})
        for bundles in self.plugins.call('find_bundles'):
            for bundle in bundles:
                self.bundles[bundle.key] = bundle
        for input_dir, directory, dirnames, filenames in self._walk():
            for fn in filenames:
                for ignore_pattern in self.config.get('ignore', ()):
                    if fnmatch(fn, ignore_pattern):
                        break
                else:
                    base, ext = os.path.splitext(fn)
                    key = os.path.join(directory, base)
                    if key.startswith('./'):
                        key = key[2:]
                    bundle = self.bundles.setdefault(key, Bundle(key, defaults.copy()))
                    bundle.add(input_dir, directory, fn)

        self.prepare_bundles()

    def _walk(self):
        for input_dir in self.input_dirs:
            for directory, dirnames, filenames in os.walk(input_dir):
                directory = os.path.relpath(directory, input_dir)

                yield (input_dir, directory, dirnames, filenames)

    def prepare_bundles(self):
        """Prepare the bundles, allow plugins to process them."""

        # Allow plugins to preprocess bundles
        for k, bundle in self.walk_bundles():
            self.middleware('preprocess_bundle', k, bundle)
            for input_dir, directory, filename in bundle:
                self.middleware('preprocess_bundle_file',
                    k, input_dir, directory, filename)
                
        # Allow bundles to prepare themselves
        for k, bundle in self.walk_bundles():
            if not bundle.meta:
                warnings.warn(f"Bundle missing metadata: {key}")
            bundle.prepare(self)
        for k, bundle in self.walk_bundles():
            bundle._prepare_contents(self)

    def add_bundles(self, bundles, replace=False):
        """Add additional bundles into the engine, mapping key->bundle."""

        for key, bundle in bundles.items():
            exists = False
            if key in self._new_bundles:
                exists = True
                existing_bundle = self._new_bundles[key]
                if replace:
                    del self._new_bundles[key]
            if key in self.bundles:
                exists = True
                existing_bundle = self.bundles[key]
                self.bundles[key] = bundle
            if exists and not replace:
                raise ValueError("duplicate bundle '%s' would replace existing" % key)
            if key not in self.bundles:
                self._new_bundles[key] = bundle

    def walk_bundles(self):
        """Iterate over (key, bundle) pairs in the engine, continuing to yield
        new bundles if they are added to the engine during the process of
        walking over the bundles.
        """

        for k, b in self.bundles.items():
            yield k, b
        first = True
        while first or self._new_bundles:
            first = False
            if self._new_bundles:
                self.bundles.update(self._new_bundles)
                for k, b in self._new_bundles.items():
                    yield k, b
                self._new_bundles = {}

    def get_bundles_by(self, *args, **kwargs):
        """Find bundles in the engine filtered and ordered as needed.
        
        order_key: The name of a meta field to order the results by
        order: 'asc' or 'desc' (default: 'asc')
        limit: The number of resuls to return (default: unlimited)
        
        Any additional keyword arguments are taken as meta field values
        which bundles must match in order to be matched.

        For example, to find all published bundles and give the most recent
        first:

            engine.get_bundles_by('updated_time', 'desc', status='published')
        """

        return filter_bundles(self.bundles.values(), *args, **kwargs)

    def get_bundle(self, *args, **kwargs):
        """With the same parameters as get_bundles_by() find exactly one
        bundle, and raise ValueError if 0 or more than 1 are found.
        """

        bundles = list(self.get_bundles_by(*args, **kwargs))
        if len(bundles) == 1:
            return bundles[0]
        elif bundles:
            raise ValueError("Found too many bundles! {}".format(
                " ".join('='.join((k, repr(v))) for (k, v)
                    in kwargs.items())
            ))
        else:
            raise ValueError("Found no bundles! {}".format(
                " ".join('='.join((k, repr(v))) for (k, v)
                    in kwargs.items())
            ))

    def render_site(self, output_dir):
        """Render all bundles to the output directory."""

        for k, bundle in self.bundles.items():
            if not bundle.meta:
                warnings.warn(f"Bundle missing metadata: {bundle.key}")
                continue
            print('from bundle', bundle.key)
            for action, output in bundle.render(self, output_dir):
                print('    ', action, output)

    def get_template(self, /, name=None, string=None):
        """Load one template by name."""

        assert name or string and not (name and string)
        if name:
            return self._jinja_env.get_template(name)
        elif string:
            return self._jinja_env.from_string(string)

    def load_plugins(self, ns='jules.plugins'):
        """Load engine plugins, and sort them by their plugin_order attribute."""

        # Loading "plain" plugins first, which are the plugin modules under jules.plugins
        plugins = load(ns)
        if not self.plugins:
            self.plugins = plugins
        else:
            self.plugins._plugins += plugins._plugins
        self.plugins._plugins.sort(key=lambda p: getattr(p, 'plugin_order', 0))

        # Load Template plugins, which inject API into templates
        self.template_plugins = load('jules.plugins', subclasses=jules.plugins.TemplatePlugin)

    def middleware(self, method, *args, **kwargs):
        """Call each loaded plugin with the same method, if it exists."""

        kwargs['engine'] = self
        return list(self.plugins.call(method, *args, **kwargs))

    def pipeline(self, method, first, *args, **kwargs):
        """Call each loaded plugin with the same method, if it exists,
        passing the return value of each as the first argument of the
        next.
        """

        kwargs['engine'] = self
        return self.plugins.pipe(method, first, *args, **kwargs)


class _BundleMeta(object):
    """This is a dict-like object for bundle meta data."""

    def __init__(self, defaults, meta):
        self.defaults = defaults
        self.meta = meta
    def __str__(self):
        return '<BundleMeta %r>' % (self.meta,)
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

class Bundle(dict):
    """Each bundle is a collection of input files, properties, and meta data."""

    def __init__(self, key, defaults=None):
        self.key = key
        self.entries = []
        self._files_by_ext = {}
        self._metadefaults = defaults or {}

    def __str__(self):
        return 'Bundle(key=%r)' % (self.key,)

    _meta = None
    @property
    def meta(self):
        """Bundle meta data loaded from a YAML file in the bundle."""

        if self._meta is None:
            data = {}
            if filename := self.by_ext('yaml'):
                data = yaml.safe_load(open(filename))
            elif filename := self.by_ext('rst'):
                rst_src = open(filename).read()
                try:
                    header, body = re.split(r'\n+[ ]*---[ ]*\n+', rst_src, 1)
                except ValueError:
                    pass
                else:
                    if header and body:
                        data = yaml.safe_load(header)
            self._meta = _BundleMeta(self._metadefaults, data)
            if 'publish_time' in self._meta:
                self._meta.setdefault('created_time', self._meta['publish_time'])
                self._meta.setdefault('updated_time', self._meta['publish_time'])
                self._meta.setdefault('year', self._meta['publish_time'].strftime('%Y'))
                self._meta.setdefault('month', self._meta['publish_time'].strftime('%Y/%m'))
        return self._meta

    @property
    def recent(self):
        """The updated, published, or created time. The first to exist is given."""

        M = self.meta
        return M['updated_time'] or M['publish_time'] or M['created_time']

    def write_meta(self):
        """Writes any changes in the meta data back to the YAML file."""

        yaml_filename = self.by_ext('yaml')
        yaml.dump(
            self._meta.meta,
            open(yaml_filename, 'w'),
            default_flow_style=False,
            )

    def __hash__(self):
        return hash(self.key)

    def __iter__(self):
        return iter(self.entries)

    def add(self, input_dir, directory, filename):
        """Add a single file to the bundle."""

        entry = (input_dir, directory, filename)
        if entry not in self.entries:
            self.entries.append(entry)
            base, ext = os.path.splitext(filename)
            self._files_by_ext[ext.lstrip('.')] = entry

    def by_ext(self, ext):
        """Find one file in the bundle with the given extension, or return None"""

        try:
            input_dir, directory, filename = self._files_by_ext[ext]
            return os.path.join(input_dir, directory, filename)
        except KeyError:
            pass
    
    @property
    def parts(self):
        return dict(self._files_by_ext)

    def get_bundles(self):
        return self

    def prepare(self, engine):
        """Prepare the bundle for the engine."""

        # Merge parent bundle defaults
        key_path = self.key.split('/')[: -1]
        while key_path:
            pkey = '/'.join(key_path)
            pbundle = engine.bundles.get(pkey)
            if pbundle is not None:
                for key, value in pbundle.meta.get('child_defaults', {}).items():
                    self.meta.setdefault(key, value)
            key_path.pop()

        self._prepare_render(engine)
        # self._prepare_contents(engine)

    def _prepare_render(self, engine):
        """Prepare the template and output name of a bundle."""

        self.template = None
        self.output_path = None

        render = self.meta.get('render')
        if render is not None:
            if render == 'jinja2':
                # Prepare template
                template_name = self.meta.get('template')
                template = None
                if template_name is not None:
                    template = engine.get_template(name=template_name)
                if template is None:
                    template_path = self.by_ext('j2')
                    if template_path:
                        with open(template_path) as f:
                            template = engine.get_template(string=f.read())
                
                # Prepare output location
                output_ext = self.meta.get('output_ext', 'html')
                path = self.key
                if path.endswith('/'):
                    path += 'index'
                if output_ext:
                    output_path = path + '.' + output_ext
                else:
                    output_path = path

                # Save them for later in the rendering stage
                self.template = template
                self.output_path = output_path

    def render(self, engine, output_dir):
        """Render the bundle to the output. "Render" can mean rendering a
        Jinja2 template or simply copying files, depending on the bundle and
        configuration.
        """

        for output in self._render_with(engine, output_dir, self.template, self.output_path):
            yield output

    def _finalize_output_path(self, output_dir, output_path):
        output_path = os.path.join(output_dir, output_path)
        ensure_path(os.path.dirname(output_path))
        if os.path.exists(output_path) and os.path.isdir(output_path):
            output_path = os.path.join(output_path, 'index.html')
        return output_path

    def _render_with(self, engine, output_dir, template, output_path):
        """Render the bundle into the output directory."""

        # If there is a template and path, render it
        if template and output_path:
            plugins = {}
            for p in engine.template_plugins:
                plugins[p.name] = p(engine)

            ctx = {}
            ctx.update(engine.context)
            ctx.update({
                'bundle': self,
                'meta': self.meta,
                'engine': engine,
                'config': engine.config,
                'bundles': engine.bundles.values(),
                'plugins': plugins,
            })
            try:
                r = template.render(ctx)
            except Exception as e:
                yield 'error', e.args[0]
            else:
                output_path = self._finalize_output_path(output_dir, output_path)
                with open(output_path, 'wb') as out:
                    out.write(r.encode('utf8'))
                yield 'render', output_path

        else:
            # If nothing to render, allow the bundle to copy content
            action = os.symlink if engine.config['debug'] else shutil.copy
            action_log = 'link' if engine.config['debug'] else 'copy'
            for input_dir, directory, filename in self._to_copy(engine):
                src_path = os.path.join(input_dir, directory, filename)
                dest_path = os.path.join(output_dir, directory, filename)
                ensure_path(os.path.dirname(dest_path))
                if os.path.exists(dest_path):
                    os.unlink(dest_path)
                action(src_path, dest_path)
                yield action_log, dest_path

    def _to_copy(self, engine):
        for input_dir, directory, filename in self:
            for ignore_pattern in engine.config.get('ignore', ()):
                if fnmatch(filename, ignore_pattern):
                    break
            else:
                yield (input_dir, directory, filename)

    content = None
    def _prepare_contents(self, engine):
        ext_plugins = {}
        content_plugins = load('jules.plugins', subclasses=jules.plugins.ContentPlugin)
        for plugin in content_plugins:
            for ext in plugin.extensions:
                ext_plugins[ext] = plugin(engine)

        content_path = None
        if 'content' in self.meta:
            content_path = os.path.abspath(os.path.expanduser(self.meta['content']))
        else:
            for input_dir, directory, filename in self:
                if content_path is not None:
                    break
                for ext in ext_plugins:
                    if filename.endswith(ext):
                        content_path = os.path.join(input_dir, directory, filename)
                        break

        src = None
        if content_path:
            try:
                src = open(content_path, 'r').read()
            except IOError:
                pass
        if not src:
            src = self.meta.get('content')
        
        if src:
            try:
                header, body = re.split(r'\n+[ ]*---[ ]*\n+', src, 1)
            except ValueError:
                body = src

            self.content = ext_plugins[ext].parse_string(body)

    def _url(self):
        key = self.key.lstrip('./')
        ext = self.meta.get('output_ext', 'html')
        if ext:
            ext = '.' + ext
        return '/' + key + ext

    def url(self):
        """Find the url the bundle will be rendered to."""

        if self.meta.get('url'):
            return self.meta['url']
        if self.template and self.output_path:
            key = self.key.lstrip('./')
            ext = self.meta.get('output_ext', 'html')
            if ext:
                ext = '.' + ext
            return "/{}{}".format(key, ext).rsplit('index.html', 1)[0]
        return None

