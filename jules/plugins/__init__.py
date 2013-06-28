class ComponentPlugin(object):
    def __init__(self, config, plugin_engine):
        self.config = config
        self.plugin_engine = plugin_engine

class QueryPlugin(object):
    def __init__(self, config, plugin_engine):
        self.config = config
        self.plugin_engine = plugin_engine
    
    def finalize(self):
        """Called after all pipelines are completely done"""
        pass