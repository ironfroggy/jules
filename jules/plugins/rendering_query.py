import os
import tempfile
import shutil

import jinja2

import jules
from jules.query import cache, unwrapping_kwargs, method_registrar
from jules import writer

class RenderingQuery(jules.plugins.QueryPlugin):
    """Query operatings for rendering results to disk."""
    methods = []
    register = method_registrar(methods)
    
    def __init__(self, *args, **kwargs):
        super(RenderingQuery, self).__init__(*args, **kwargs)
        self.env = self.make_env()
        self.tempdir = tempfile.mkdtemp(suffix='-jules')
        self.writer = writer.URLWriter(self.tempdir)

    def make_env(self):
        env = jinja2.Environment(
            extensions=['jinja2.ext.do'],
            loader=jinja2.loaders.FileSystemLoader(self.config['templates']),
        )

        env.filters.update(
            (filter_name, func)
            for filter_name, func in vars(jules.filters).iteritems()
            if not filter_name.startswith('_'))
        
        return env
    
    @register
    @unwrapping_kwargs
    def render_each(self, results, template, url):
        url = jinja2.Template(url)
        # only called `template` in args for API reasons
        template_name = template
        template = self.env.get_template(template_name)
        for item in results:
            print "RENDER %s(%s) --> %s" % (template_name, item, url.render(item))
            with self.writer.urlopen(url.render(item)) as f:
                f.write(template.render(item))
            
            yield item
    
    @register
    @unwrapping_kwargs
    def render_all(self, results, template, url, kw='items'):
        results = cache(results)
        url = jinja2.Template(url)
        # only called `template` in args for API reasons
        template_name = template
        template = self.env.get_template(template_name)
        item = {kw: results}

        print "RENDER %s(%s) --> %s" % (template_name, item, url.render(item))
        with self.writer.urlopen(url.render(item)) as f:
            f.write(template.render(item))

        return results
    
    def finalize(self):
        out = self.config['output_dir']
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
    