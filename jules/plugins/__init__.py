class ComponentPlugin(object):
    def __init__(self, engine):
        self.engine = engine

class QueryPlugin(object):
    def __init__(self, engine):
        self.engine = engine
    
    def finalize(self):
        """Called after all pipelines are completely done"""
        pass