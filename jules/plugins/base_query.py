import itertools
import code

import jinja2

import jules
from jules.query import cache, unwrapping_kwargs, method_registrar

def unpack_components(components, require_components, maybe_components):
    d = {}
    for k in itertools.chain(require_components, maybe_components):
        d[k] = components.get(k, None)
    return d

def precompile(exprs):
    return [compile(e, '<query>', 'eval') for e in exprs]

class BaseQuery(jules.plugins.QueryPlugin):
    """Basic querying operations"""
    methods = []
    register = method_registrar(methods)
    
    @register
    @unwrapping_kwargs
    def select(self,
        results,
        require_components = (),
        maybe_components = (),
        forbid_components = ()):
    
        for bundle in results:
            if not all(comp in bundle.components for comp in require_components):
                continue
            if any(comp in forbid_components for comp in bundle.components):
                continue
            # FIXME: find reporting mechanism for bundles??? maybe set to
            #        accessed_bundles attribute of self or something.
            yield unpack_components(bundle.components, require_components, maybe_components)

    @register
    @unwrapping_kwargs
    def order_by(self, results, key, descending=False):
        key, = precompile([key])
        return sorted(results,
            reverse=descending,
            key=lambda item: eval(key, {}, item))
    
    @register
    def where(self, results, clauses):
        clauses = precompile(clauses)
        for item in results:
            if all(eval(clause, {}, item) for clause in clauses):
                yield item
    
    @register
    def limit(self, results, n):
        for item, _ in itertools.izip(results, xrange(n)):
            yield item
    
    @register
    def group_by_in(self, results, expr):
        """
        Given an iterable of bundles, for each member even one bundle has in `expr`,
        group together all bundles that also have that member in `expr`.
        
        `expr` has to return an object supporting iteration and the `in` operator,
        for every bundle. Everything in that object must support hashing.
        """
        results = cache(results)
        expr, = precompile([expr])
        valuesets = [eval(expr, {}, item) for item in results]
        return self._group_by(results, valuesets)

    @register
    def group_by_eq(self, results, expr):
        """Traditional group-by"""
        results = cache(results)
        expr, = precompile([expr])
        valuesets = [[eval(expr, {}, item)] for item in results]
        return self._group_by(results, valuesets)

    def _group_by(self, results, valuesets):
        """The backend implementation of group_by_in (and eq, secretly.)
        
        Requires that the resultset be cached as a list (not an iterator)
        """
        grouped_values = set()
        for valueset in valuesets:
            for value in valueset:
                if value in grouped_values:
                    continue
                grouped_values.add(value)
                
                group = [item
                    for item, valueset in itertools.izip(results, valuesets)
                    if value in valueset]
                
                yield {'group': group, 'key': value}
    
    @register
    def rename(self, results, renames):
        for item in results:
            yield {new_k: item[old_k] for new_k, old_k in renames.iteritems()}
    
    @register
    def count(self, results, count_key):
        for i, item in enumerate(results):
            d = {}
            d.update(item)
            d[count_key] = i
            yield d
    
    @register
    def debug(self, results, _command):
        # TODO: optional print. Instead, we ignore command...
        results = list(results)
        code.interact(
            "Debugging all results, available as local variable `results`.",
            local={'results': results})
        return results
    
    @register
    def debug_each(self, results, _command):
        # TODO: optional print. Instead, we ignore command...
        for i, item in enumerate(results):
            code.interact(
                "Debugging row %d, available as local variable `result`." % i,
                local={'result': item})
            yield item

    def finalize(self):
        pass