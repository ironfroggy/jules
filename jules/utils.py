import os
from datetime import date, datetime

from straight.plugin import load


def ensure_path(path):
    path_parts = os.path.split(path)
    for i in range(len(path_parts)):
        subpath = os.path.join(*path_parts[: i + 1 ])
        if subpath and not os.path.exists(subpath):
            os.mkdir(subpath)

class KeyConflictError(ValueError):
    pass

def named_keywords(*args, **kwargs):
    return merge(dict(zip(args, args)), kwargs)

def merge(d1, d2):
    d = {}
    d.update(d1)
    for k, v in d2.iteritems():
        if k in d:
            raise KeyConflictError(k)
        d[k] = v
    return d


class Namespace(dict):
    def __repr__(self):
        return "%s(%s)" % (
            type(self).__name__,
            super(Namespace, self).__repr__())

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            return super(Namespace, self).__getattribute__(name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]

class CircularDependencyError(ValueError): pass

def topsort(G):
    """Topological sorting of a graph.
    
    G is of the form {key: set([predecessor_key, ...]), ...}
    (i.e. a directed adjacency list representation, with the edges representing
     incoming edges, rather than outgoing)
    """
    
    G = dict((k, set(v)) for k, v in G.iteritems())
    # this new G lets us cut out elements from the graph
    while True:
        # find key with no incoming edges
        for k, deps in G.iteritems():
            if not deps:
                yield k
                del_key(G, k)
                break
        else:
            # couldn't find any keys without dependencies
            if G:
                raise CircularDependencyError(list(G))
            else:
                return

def del_key(G, k):
    """Remove a key from a graph"""
    del G[k]
    for s in G.itervalues():
        if k in s: s.remove(k)
