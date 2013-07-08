from straight.plugin import load

import jules
from jules.plugins import ComponentPlugin, BaseJulesPlugin

jules.add_namespace(__package__)

class PostComponent(ComponentPlugin):
    name = 'post'
    basenames = ['post']
    component_dependencies = ['meta']
    
    def __init__(self, *args, **kwargs):
        super(PostComponent, self).__init__(*args, **kwargs)
        
        # FIXME: conflict detection
        self.ext_plugins = ext_plugins = {}
        # FIXME: content plugins don't work consistently with rest of plugins.
        #        i.e. they're instantiated once per time, and in addition,
        #        have to be present in the right namespace package.
        content_plugins = load(
            'jules.plugins.post',
            subclasses=PostParserPlugin)
        for plugin in content_plugins:
            for ext in plugin.extensions:
                ext_plugins[ext] = plugin
    
    def maybe_load(self, components, post):
        meta = components['meta']
        post_ext, post_path = post
        
        try:
            return self.engine.plugins.produce_new_instance(
                self.ext_plugins[post_ext],
                open(post_path),
                meta)
        except KeyError:
            return None

class PostParserPlugin(BaseJulesPlugin):
    def __init__(self, f, meta, *args, **kwargs):
        self._f = f
        self._content = None
        self.meta = meta
        self.content_loaded = False
        super(PostParserPlugin, self).__init__(*args, **kwargs)
    
    def get_content(self):
        if self.content_loaded:
            return self._content
        with self._f:
            return self.parse_string(self._f.read())

##class TemplatePlugin(object):

    ##def __init__(self, engine):
        ##self.engine = engine