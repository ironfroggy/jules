import os

from straight.plugin import load
from jules.utils import middleware, pipeline, maybe_call


class JulesEngine(object):

    def __init__(self):
        self.input_dirs = []
        self.bundles = {}
        self.context = {}
        self.plugins = []

    def load_plugins(self, ns='jules.plugins'):
        self.plugins = load(ns)
        self.plugins.sort(key=lambda p: getattr(p, 'plugin_order', 0))

    def middleware(self, method, *args, **kwargs):
        """Call each loaded plugin with the same method, if it exists."""
        kwargs['engine'] = self
        for plugin in self.plugins:
            maybe_call(plugin, method, *args, **kwargs)

    def pipeline(self, method, first, *args, **kwargs):
        """Call each loaded plugin with the same method, if it exists,
        passing the return value of each as the first argument of the
        next.
        """

        kwargs['engine'] = self
        r = None
        for plugin in self.plugins:
            r = maybe_call(plugin, method, first, *args, **kwargs)
            if r is not None:
                first = r
        return r

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
        for bundles in middleware('find_bundles'):
            for bundle in bundles:
                self.bundles[bundle.key] = bundle
        for input_dir, directory, dirnames, filenames in self._walk():
            for fn in filenames:
                base, ext = os.path.splitext(fn)
                key = os.path.join(directory, base)
                bundle = self.bundles.setdefault(key, Bundle(key))
                bundle.add(input_dir, directory, fn)


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


class BundleFactory(Bundle):

    def get_bundles(self, **kwargs):
        bundle = Bundle(self.key.format(**kwargs))
        bundle.entries = self.entries
        bundle._files_by_ext = self._files_by_ext
        bundle.update(self)
