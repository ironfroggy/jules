class ContentPlugin(object):

    def __init__(self, engine):
        self.engine = engine

    def parse(self, content_file):
        src = content_file.read()
        return self.parse_string(src)
