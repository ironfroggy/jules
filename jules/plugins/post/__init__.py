from straight.plugin import load

from jules.plugins import ComponentPlugin

class PostComponent(ComponentPlugin):
    name = 'post'
    basenames = ['post']
    
    def __init__(self, *args, **kwargs):
        super(PostComponent, self).__init__(*args, **kwargs)
        
        # FIXME: conflict detection
        self.ext_plugins = ext_plugins = {}
        content_plugins = load(
            'jules.plugins.post',
            subclasses=PostParserPlugin)
        for plugin in content_plugins:
            for ext in plugin.extensions:
                ext_plugins[ext] = plugin(self.config, self.plugin_engine)
    
    def maybe_load(self, post):
        (post_ext, post_f) = post
        with open(post_f) as f:
            # TODO: more than just loading.
            # FIXME: better plugin organization
            return self.plugins.first("load_document", post_ext, f)
    
    def maybe_load(self, post):
        post_ext, post_path = post
        
        try:
            return self.ext_plugins[post_ext].parse(open(post_path))
        except (IOError, KeyError) as e:
            return None

class PostParserPlugin(object):
    def __init__(self, config, plugin_engine):
        self.config = config
        self.plugin_engine = plugin_engine

    def parse(self, content_file):
        src = content_file.read()
        return self.parse_string(src)


##class TemplatePlugin(object):

    ##def __init__(self, engine):
        ##self.engine = engine