from straight.plugin import load

import jules
from jules.plugins import ComponentPlugin

jules.add_namespace(__package__)

class PostComponent(ComponentPlugin):
    name = 'post'
    basenames = ['post']
    
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
    
    def maybe_load(self, post):
        post_ext, post_path = post
        
        try:
            return self.engine.plugins.produce_new_instance(
                self.ext_plugins[post_ext],
                open(post_path))
        except KeyError:
            return None

class PostParserPlugin(object):
    def __init__(self, f, engine):
        self._f = f
        self._content = None
        self.content_loaded = False
    
    def get_content(self):
        if self.content_loaded:
            return self._content
        with self._f:
            return self.parse_string(self._f.read())

##class TemplatePlugin(object):

    ##def __init__(self, engine):
        ##self.engine = engine