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
        content_plugins = self.engine.plugins.produce_instances(
            PostParserPlugin)
        for plugin in content_plugins:
            for ext in plugin.extensions:
                ext_plugins[ext] = plugin
    
    def maybe_load(self, components, post):
        meta = components['meta']
        post_ext, post_path = post
        
        post = open(post_path)
        try:
            return self.ext_plugins[post_ext].parse_post(meta, post.read())
        except KeyError:
            return None
        finally:
            post.close()

class PostParserPlugin(BaseJulesPlugin):
    pass

##class TemplatePlugin(object):

    ##def __init__(self, engine):
        ##self.engine = engine