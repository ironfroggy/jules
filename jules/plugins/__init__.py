class BaseJulesPlugin(object):
    dependencies = ()
    
    # TODO: implement *dep_instances ?
    def __init__(self, engine):
        self.engine = engine

class ComponentPlugin(BaseJulesPlugin):
    pass

class QueryPlugin(BaseJulesPlugin):
    pass

class EnginePlugin(BaseJulesPlugin):
    def initialize(self):
        """Called before the Jules engine renders content"""
    
    def finalize(self):
        """Called as the jules engine finalizes content."""