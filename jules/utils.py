import os

from straight.plugin import load


def maybe_call(obj, name, *args, **kwargs):
    method = getattr(obj, name, None)
    if method is not None:
        return method(*args, **kwargs)

def middleware(method, *args, **kwargs):
    plugins = load('jules.plugins')
    plugins.sort(key=lambda p: getattr(p, 'plugin_order', 0))
    results = []
    for plugin in plugins:
        r = maybe_call(plugin, method, *args, **kwargs)
        if r is not None:
            results.append(r)
    return results

def pipeline(method, first, *args, **kwargs):
    plugins = load('jules.plugins')
    plugins.sort(key=lambda p: getattr(p, 'plugin_order', 0))
    for plugin in plugins:
        new_first = maybe_call(plugin, method, first, *args, **kwargs)
        if new_first is not None:
            first = new_first
    return first

def first(method, *args, **kwargs):
    plugins = load('jules.plugins')
    plugins.sort(key=lambda p: getattr(p, 'plugin_order', 0))
    for plugin in plugins:
        r = maybe_call(plugin, method, *args, **kwargs)
        if r is not None:
            return r

def ensure_path(path):
    path_parts = os.path.split(path)
    for i in xrange(len(path_parts)):
        subpath = os.path.join(*path_parts[: i + 1 ])
        if not os.path.exists(subpath):
            os.mkdir(subpath)
