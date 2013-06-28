import functools
import ast

import jules

def result(f):
    return lambda *args, **kwargs: ResultSet(f(*args, **kwargs))

class QueryEngine(object):
    def __init__(self, engine):
        self.plugins = (engine.plugins
            .load(subclasses=jules.plugins.QueryPlugin)
            .produce(engine))
        self.dispatch_map = {}
        for plugin in self.plugins:
            for method_name in plugin.methods:
                if method_name in self.dispatch_map:
                    raise jules.plugins.PluginConflictError(
                        "Query plugins %s and %s conflict on %r"
                        % (self.dispatch_map[method_name].im_class,
                           plugin.__class__,
                           method_name))
                self.dispatch_map[method_name] = getattr(plugin, method_name)
    
    def dispatch(self, method_name, *args, **kwargs):
        return self.dispatch_map[method_name](*args, **kwargs)
    
    def finalize(self):
        for result in self.plugins.call("finalize"):
            pass

class ResultSet(object):
    def __init__(self, engine, seq):
        self._engine = engine
        self._seq = seq
    
    def __iter__(self):
        return iter(self._seq)
    
    def __getattr__(self, name):
        try:
            return self.get_method(name)
        except KeyError:
            raise AttributeError(name)

    def get_method(self, name):
        method = self._engine.dispatch_map[name]
        def method_wrapper(*args, **kwargs):
            new_seq = method(self._seq, *args, **kwargs)
            return ResultSet(self._engine, new_seq)
        return method_wrapper

# some utility functions for plugins
def method_registrar(methods):
    def register(f):
        methods.append(f.__name__)
        return f
    return register

def cache(iterable):
    """Convert an iterator to a repeatable iterable.
    
    If a known repeatable iterable type is passed in, then as an optimization,
    that will be returned, but this is not guaranteed.
    """
    if isinstance(iterable, (list, tuple)):
        return iterable
    return list(iterable)

def unwrapping_kwargs(f):
    @functools.wraps(f)
    def unwrapped_f(self, results, *args, **kwargs):
        new_kwargs = {}
        for d in args:
            new_kwargs.update(d)
        new_kwargs.update(kwargs)
        return f(self, results, **new_kwargs)
    return unwrapped_f

