import os
import tempfile
import shutil

import jinja2

import jules
from jules.query import cache, unwrapping_kwargs, method_registrar
from jules import writer


class CanonConflictError(Exception): pass

class Renderer(jules.plugins.QueryPlugin, jules.plugins.EnginePlugin):
    """Query operatings for rendering results to disk.
    
    A basic problem is that posts need to know canonical URLs, but canonical
    URLs are generated after posts. To solve this, we look at the URLs first,
    and only then do we render the templates and write out the actual data.
    
    Steps:
     * Collect URL information
       This is done during the pipeline/query phase. To be precise, we collect:
        
        - what URLs get rendered with what templates, data.
        - what URLs are canonical for what names.
     * Render to disk.
       This is done during the finalization phase of the EnginePlugin,
       using the final_render() method.
     * Put rendered data into final location.
       This is also done during finalization, but in final_move()
    """
    
    methods = []
    register = method_registrar(methods)
    
    def __init__(self, *args, **kwargs):
        super(Renderer, self).__init__(*args, **kwargs)
        self.env = self.make_env()

        self.url_canon = {} # map names -> (url, title)
        self.name_canon = {} # map urls -> (name, title)
        self.render_actions = [] # [(url, template, item)]

    def make_env(self):
        env = jinja2.Environment(
            extensions=['jinja2.ext.do'],
            loader=jinja2.loaders.FileSystemLoader(
                self.engine.config['templates']),
            undefined=jinja2.StrictUndefined
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
            if canonical_for is not None:
                self.update_canon(
                    canonical_for.render(item),
                    self.maybe_render(canonical_title, item),
                    final_url)
            self.render_actions.append((final_url, template, item))

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
        if canonical_for is not None:
            canonical_for = self.env.from_string(canonical_for).render(item)
            canonical_title = self.maybe_render(self.maybe_template(canonical_title), item)
            self.update_canon(canonical_for, canonical_title, final_url)

        self.render_actions.append((final_url, template, item))

        return results
    
    def final_render(self):
        tempdir = tempfile.mkdtemp(suffix='-jules')
        urlwriter = writer.URLWriter(tempdir)
        for url, template, item in self.render_actions:
            with urlwriter.urlopen(url) as f:
                f.write(template.render(item))

        del self.render_actions[:]
        return tempdir
    
    def finalize(self):
        self.final_move(self.final_render())

    def final_move(self, tempdir):
        out = self.engine.config['output_dir']
        temp_storage = tempfile.mkdtemp(suffix='-jules')
        
        # race conditions ahoy, unavoidable, don't care.
        # should I even bother with this?
        old_out = None
        if os.path.isdir(out):
            old_out = os.path.join(temp_storage, os.path.basename)
            shutil.move(out, old_out)
        try:
            shutil.move(tempdir, out)
        finally:
            if old_out is not None:
                shutil.move(old_out, out)

    def update_canon(self, name, title, url):
        try:
            old_url, old_title = self.url_canon[name]
        except KeyError:
            pass
        else:
            if old_url == url:
                raise CanonConflictError(
                    "Resources want identical names and URL: "
                    "name %r and URL %r (%s and %s)"
                    % (name, url, old_title, title))
            raise CanonConflictError(
                "The resources at URL %r (%s) and URL %r (%s) both "
                "want the name %r"
                % (old_url, old_title, url, title, name))
        
        try:
            old_name, old_title = self.name_canon[url]
        except KeyError:
            pass
        else:
            raise CanonConflictError(
                "The resources %r (%s) and %r (%s) both "
                "want the URL %r"
                % (old_name, old_title, name, title, url))
        
        self.url_canon[name] = url, title
        self.name_canon[url] = name, title

    def maybe_template(self, t):
        if t is not None:
            return self.env.from_string(t)

    @staticmethod
    def maybe_render(t, *args, **kwargs):
        if t is not None:
            return t.render(*args, **kwargs)

def fmt_title(t):
    return "no title" if t is None else "title %r" % t