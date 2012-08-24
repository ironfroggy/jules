from __future__ import print_function


import os
import re
import shutil
from fnmatch import fnmatch

import yaml
from straight.plugin import load
import jinja2

import jules
from jules.utils import ensure_path, filter_bundles


PACKAGE_DIR = os.path.dirname(__file__)


class JulesEngine(object):

    def __init__(self, src_path):
        self.src_path = src_path
        self.input_dirs = [os.path.join(PACKAGE_DIR, 'packs', 'jules')]
        self.bundles = {}
        self._new_bundles = {}
        self.context = {}
        self.config = {}

    def load_config(self):
        config_path = os.path.join(self.src_path, 'site.yaml')
        if os.path.exists(config_path):
            with open(config_path) as f:
                self.config.update(yaml.load(f))
        else:
            raise ValueError("No configuration file found. Looking for site.yaml at `{}`.".format(self.src_path))

    def prepare(self):
        self.load_config()
        self.load_plugins()

        for pack_def in self.config.get('packs', ()):
            pack_type, pack_name = pack_def.split(':', 1)
            if pack_type == 'jules':
                self.input_dirs.append(os.path.join(PACKAGE_DIR, 'packs', pack_name))
            elif pack_type == 'dir':
                self.input_dirs.append(os.path.abspath(pack_name))

        self._jinja_env = jinja2.Environment(
            loader = jinja2.loaders.FileSystemLoader(self.input_dirs),
        )

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

    def prepare_bundles(self):
        for k, bundle in self.walk_bundles():
            self.middleware('preprocess_bundle', k, bundle)
            for input_dir, directory, filename in bundle:
                self.middleware('preprocess_bundle_file',
                    k, input_dir, directory, filename)
            bundle.prepare(self)

    def add_bundles(self, bundles):
        self._new_bundles.update(bundles)

    def walk_bundles(self):
        first = True
        while first or self._new_bundles:
            first = False
            if self._new_bundles:
                self.bundles.update(self._new_bundles)
                self._new_bundles = {}
            for k, b in self.bundles.iteritems():
                yield k, b

    def get_bundles_by(self, *args, **kwargs):
        return filter_bundles(self.bundles.values(), *args, **kwargs)

    def get_bundle(self, *args, **kwargs):
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
        for k, bundle in self.bundles.items():
            print('render', k, bundle)
            if bundle.template and bundle.output_path:
                r = bundle.template.render({
                    'bundle': bundle,
                    'meta': bundle.meta,
                    'engine': self,
                    'config': self.config,
                    'bundles': self.bundles.values(),
                })
                output_path = os.path.join(output_dir, bundle.output_path)
                ensure_path(os.path.dirname(output_path))
                with open(output_path, 'w') as out:
                    out.write(r)
            else:
                for input_dir, directory, filename in bundle:
                    src_path = os.path.join(input_dir, directory, filename)
                    dest_path = os.path.join(output_dir, directory, filename)
                    ensure_path(os.path.dirname(dest_path))
                    shutil.copy(src_path, dest_path)

    def get_template(self, name):
        return self._jinja_env.get_template(name)

    def load_plugins(self, ns='jules.plugins'):
        self.plugins = load(ns)
        self.plugins._plugins.sort(key=lambda p: getattr(p, 'plugin_order', 0))

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

    def _walk(self):
        for input_dir in self.input_dirs:
            for directory, dirnames, filenames in os.walk(input_dir):
                directory = os.path.relpath(directory, input_dir)

                yield (input_dir, directory, dirnames, filenames)

    def walk_input_directories(self):
        for input_dir, directory, dirnames, filenames in self._walk():
            for d in dirnames:
                yield input_dir, directory, d

    def walk_input_files(self):
        for input_dir, directory, dirnames, filenames in self._walk():
            for f in filenames:
                yield input_dir, directory, f

    def find_bundles(self):
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
                    bundle = self.bundles.setdefault(key, Bundle(key))
                    bundle.add(input_dir, directory, fn)

    def find_file(self, filepath):
        filepath = os.path.relpath(filepath)
        for k in self.bundles:
            for input_dir, directory, filename in self.bundles[k]:
                if filepath == os.path.relpath(os.path.join(directory, filename)):
                    return self.bundles[k], os.path.join(input_dir, directory, filename)
        return None, None


class Bundle(dict):

    def __init__(self, key):
        self.key = key
        self.entries = []
        self._files_by_ext = {}

    meta = property(lambda self: self.setdefault('meta', {}))

    def __hash__(self):
        return hash(self.key)

    def __iter__(self):
        return iter(self.entries)

    def add(self, input_dir, directory, filename):
        self.entries.append((input_dir, directory, filename))
        base, ext = os.path.splitext(filename)
        self._files_by_ext[ext.lstrip('.')] = (input_dir, directory, filename)

    def by_ext(self, ext):
        try:
            input_dir, directory, filename = self._files_by_ext[ext]
            return os.path.join(input_dir, directory, filename)
        except KeyError:
            pass

    def get_bundles(self):
        return self

    def prepare(self, engine):
        self._prepare_render(engine)
        self._prepare_contents()

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
                    template = engine.get_template(template_name)
                if template is None:
                    template_path = self.by_ext('j2')
                    with open(template_path) as f:
                        template = jinja2.Template(f.read())
                
                # Prepare output location
                output_ext = self.meta.get('output_ext', 'html')
                path = self.key
                if path.endswith('/'):
                    path += 'index'
                output_path = path + '.' + output_ext

                # Save them for later in the rendering stage
                self.template = template
                self.output_path = output_path

    content = None
    def _prepare_contents(self):
        ext_plugins = {}
        content_plugins = load('jules.plugins', subclasses=jules.plugins.ContentPlugin)
        for plugin in content_plugins:
            for ext in plugin.extensions:
                ext_plugins[ext] = plugin()

        content_path = None
        if 'content' in self.meta:
            content_path = os.path.abspath(os.path.expanduser(self.meta['content']))
        else:
            for input_dir, directory, filename in self:
                for ext in ext_plugins:
                    if filename.endswith(ext):
                        content_path = os.path.join(input_dir, directory, filename)

        if content_path:
            try:
                self.content = ext_plugins[ext].parse(open(content_path))
            except IOError:
                pass
        if not self.content:
            src = self.meta.get('content')
            if src:
                self.content = ext_plugins[ext].parse_string(src)


    def _url(self):
        key = self.key.lstrip('./')
        return '/' + key + ".html"

    def url(self):
        if self.template and self.output_path:
            return self._url().rsplit('index.html', 1)[0]
        return None


class BundleFactory(Bundle):

    def get_bundles(self, **kwargs):
        bundle = Bundle(self.key.format(**kwargs))
        bundle.entries = self.entries
        bundle._files_by_ext = self._files_by_ext
        bundle.update(self)
