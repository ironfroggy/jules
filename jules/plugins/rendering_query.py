import jinja2
import jules
from jules.query import cache, unwrapping_kwargs, method_registrar

class RenderingQuery(jules.plugins.QueryPlugin):
    """Basic querying operations"""
    methods = []
    register = method_registrar(methods)
    
    def __init__(self, *args, **kwargs):
        super(RenderingQuery, self).__init__(*args, **kwargs)
        self.env = self.make_env()

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
        results = cache(results)
        url = jinja2.Template(url)
        for item in results:
            print "RENDER %s(%s) --> %s" % (template, item, url.render(item))
        return results
    
    @register
    @unwrapping_kwargs
    def render_all(self, results, template, url, kw='items'):
        results = cache(results)
        url = jinja2.Template(url)
        item = {kw: results}
        print "RENDER %s(%s) --> %s" % (template, item, url.render(item))
        return results
    
    def finalize(self):
        print "FINALIZE RENDERING"