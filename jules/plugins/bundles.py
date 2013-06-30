import os
from fnmatch import fnmatch
import functools

from jules import Bundle
from jules.plugins import ComponentPlugin, BundleFinderPlugin

class DefaultBundleFinder(BundleFinderPlugin):
    def is_ignored_bundle(self, bundle):
        for ignore_pattern in self.engine.config.get('ignore', ()):
            if fnmatch(bundle[1], ignore_pattern):
                return True
        return False

    def find_bundles(self):
        """Find all bundles in the input directories.
        
        A bundle is a directory that contains files relevant to the bundle.
        Any directory found in any of the input directories is a bundle, unless it's
        listed to be ignored.
        """
        defaults = self.engine.config.get('bundle_defaults', {})

        for input_dir in self.engine.input_dirs:
            files, bundles = _potential_bundles(input_dir)
            bundles = [b for b in bundles if not self.is_ignored_bundle(b)]
            for (path, name) in bundles:
                prefix, key = os.path.split(path)
                directory = os.path.basename(prefix)

                bundle = Bundle(key, directory, path, defaults.copy())
                yield bundle

def _paths(parent, paths):
    return [(os.path.join(parent, p), p) for p in paths]

def _potential_bundles(input_dir):
    """Given a directory containing bundles, return a 2-tuple of:
      - all the non-bundle filenames in that directory,
      - all the possible bundles' filenames
    
    Every filename is iteself provided as a 2-tuple of (path, relpath),
    where relpath is relative to the input_dir (i.e. just the basename,
    at least for now). `path` is a valid path (relative or absolute) that one
    can use open() with.
    """
    parent, dirnames, filenames = os.walk(input_dir).next()
    return (_paths(parent, filenames), _paths(parent, dirnames))

class MetaComponent(ComponentPlugin):
    name = 'meta'
    basenames = ['meta']
    
    def maybe_load(self, meta):
        (meta_ext, meta_f) = meta
        with open(meta_f) as f:
            if meta_ext == '.json':
                return json.load(f)
            elif meta_ext == '.yaml':
                import yaml
                return yaml.safe_load(f)
