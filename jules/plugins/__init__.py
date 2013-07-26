from jules import utils

class PluginDefinitionError(Exception):
    pass

class PluginConflictError(Exception):
    pass

class BaseJulesPlugin(object):
    dependencies = None
    config = None
    
    def __init__(self, engine, deps, conf):
        self.engine = engine
        for k, v in deps.iteritems():
            setattr(self, k, v)

        self.config = utils.Namespace(conf)
        
        self.init()
    
    def init(self):
        """Convenience init method, instead of that super() nonsense."""

class ComponentPlugin(BaseJulesPlugin):
    component_dependencies = ()

class QueryPlugin(BaseJulesPlugin):
    pass

class EnginePlugin(BaseJulesPlugin):
    def initialize(self):
        """Called before the Jules engine renders content"""
    
    def finalize(self):
        """Called as the jules engine finalizes content."""

class BundleFinderPlugin(BaseJulesPlugin):
    def find_bundles(self):
        """Return an iterable of Bundle instances"""