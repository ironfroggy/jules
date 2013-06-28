class ComponentPlugin(object):
    def __init__(self, engine):
        self.engine = engine

class QueryPlugin(object):
    def __init__(self, engine):
        self.engine = engine

class EnginePlugin(object):
    def __init__(self, engine):
        self.engine = engine
    
    def initialize(self):
        """Called before the Jules engine renders content"""
    
    def finalize(self):
        """Called as the jules engine finalizes content."""