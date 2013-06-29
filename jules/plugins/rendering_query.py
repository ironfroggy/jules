import os
import tempfile
import shutil

import jinja2

import jules
from jules.query import cache, unwrapping_kwargs, method_registrar
from jules import writer


# FIXME: rewrite into multiple phases?
#        phase 1: collect URL information:
#                  - what URLs get rendered with what data,
#                  - what URLs are canonical for what names
#        phase 2: render to disk:
#                  - render posts from reST etc. to strings (HELP, HOW DO?)
#                  - render posts from strings into the templates
#        phase 3: put rendered data into final location.
#
# The basic problem is that posts need to know canonical URLs, but canonical
# URLs are generated after posts...
class Renderer(jules.plugins.QueryPlugin, jules.plugins.EnginePlugin):
    """Query operatings for rendering results to disk."""
    methods = []
    register = method_registrar(methods)
    
    def __init__(self, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)
        self.env = self.make_env()
        self.tempdir = tempfile.mkdtemp(suffix='-jules')
        self.writer = writer.URLWriter(self.tempdir)
        self.url_canon = {}

    def make_env(self):
        env = jinja2.Environment(
            extensions=['jinja2.ext.do'],
            loader=jinja2.loaders.FileSystemLoader(
                self.engine.config['templates']),
        )

        env.filters.update(
            (filter_name, func)
            for filter_name, func in vars(jules.filters).iteritems()
            if not filter_name.startswith('_'))
        
        return env
    
    def item_withbundles(self, item):
        d = dict(
            bundles=self.engine.query_engine.resultset(
                self.engine.bundles.values()))
        d.update(item)
        return d
    
    @register
    @unwrapping_kwargs
    def render_each(self, results, template, url, canonical_for=None):
        url = jinja2.Template(url)
        if canonical_for is not None:
            canonical_for = jinja2.Template(canonical_for)
        # only called `template` in args for API reasons
        template_name = template
        template = self.env.get_template(template_name)
        for item in results:
            item = self.item_withbundles(item)
            final_url = url.render(item)
            if canonical_for is not None:
                self.update_canon(canonical_for.render(item), final_url)

            with self.writer.urlopen(final_url) as f:
                f.write(template.render(item))

            yield item
    
    @register
    @unwrapping_kwargs
    def render_all(self, results, template, url, kw='items', canonical_for=None):
        results = cache(results)
        # only called `template` in args for API reasons
        template_name = template
        template = self.env.get_template(template_name)
        item = self.item_withbundles({kw: results})
        final_url = jinja2.Template(url).render(item)
        if canonical_for is not None:
            canonical_for = jinja2.Template(canonical_for).render(item)
            self.update_canon(canonical_for, final_url)

        with self.writer.urlopen(final_url) as f:
            f.write(template.render(item))

        return results
    
    def finalize(self):
        out = self.engine.config['output_dir']
        temp_storage = tempfile.mkdtemp(suffix='-jules')
        
        # race conditions ahoy, unavoidable, don't care.
        # should I even bother with this?
        old_out = None
        if os.path.isdir(out):
            old_out = os.path.join(temp_storage, os.path.basename)
            shutil.move(out, old_out)
        try:
            shutil.move(self.tempdir, out)
        finally:
            if old_out is not None:
                shutil.move(old_out, out)
    