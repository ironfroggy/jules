import os
import tempfile
import shutil

import jinja2

import jules
from jules.query import cache, unwrapping_kwargs, method_registrar
from jules import writer, utils


class CanonConflictError(Exception): pass

class QueryRenderer(jules.plugins.QueryPlugin, jules.plugins.rendering.RenderingPlugin):
    
    config = utils.named_keywords('templates')
    
    methods = []
    register = method_registrar(methods)
    
    def init(self):
        self.config.setdefault('templates',
            [os.path.join(self.engine.src_path, 'templates')])
        
        self.render_actions = [] # [(url, canon, renderer, (item,))]
        
        self.env = jinja2.Environment(
            extensions=['jinja2.ext.do'],
            loader=jinja2.loaders.FileSystemLoader(
                self.config.templates),
            undefined=jinja2.StrictUndefined
        )

        self.env.filters.update(
            (filter_name, func)
            for filter_name, func in vars(jules.filters).iteritems()
            if not filter_name.startswith('_'))
        
    
    def item_withbundles(self, item):
        d = dict(
            bundles=self.engine.query_engine.resultset(
                self.engine.bundles.values()))
        d.update(item)
        return d

    @register
    @unwrapping_kwargs
    def render_each(self, results, template, url, canonical_for=None, canonical_title=None):
        # FIXME: fail if canonical_title passed but not canonical_for
        url = self.env.from_string(url)
        canonical_for = self.maybe_template(canonical_for)
        canonical_title = self.maybe_template(canonical_title)
        # only called `template` in args for API reasons
        template_name = template
        template = self.env.get_template(template_name)
        for item in results:
            item = self.item_withbundles(item)
            final_url = url.render(item)
            canonical = None
            if canonical_for is not None:
                canonical = (
                    canonical_for.render(item),
                    self.maybe_render(canonical_title, item))
            self.render_actions.append((
                final_url,
                canonical,
                TemplateFileRenderer(template),
                (item,)))

            yield item

    @register
    @unwrapping_kwargs
    def render_all(self, results, template, url, kw='items', canonical_for=None, canonical_title=None):
        results = cache(results)
        # only called `template` in args for API reasons
        template_name = template
        template = self.env.get_template(template_name)
        item = self.item_withbundles({kw: results})
        final_url = self.env.from_string(url).render(item)
        canonical = None
        if canonical_for is not None:
            canonical_for = self.env.from_string(canonical_for).render(item)
            canonical_title = self.maybe_render(self.maybe_template(canonical_title), item)
            canonical = (canonical_for, canonical_title)

        self.render_actions.append((
            final_url,
            canonical,
            TemplateFileRenderer(template),
            (item,)))

        return results
    
    def get_render_actions(self):
        rv = self.render_actions
        self.render_actions = []
        return rv
    
    def maybe_template(self, t):
        if t is not None:
            return self.env.from_string(t)

    @staticmethod
    def maybe_render(t, *args, **kwargs):
        if t is not None:
            return t.render(*args, **kwargs)

class TemplateFileRenderer(object):
    def __init__(self, template):
        self.template = template
    
    def render(self, f, *args):
        for s in self.template.generate(*args):
            f.write(s)
