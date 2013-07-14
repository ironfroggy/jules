from jules.plugins.post import PostParserPlugin

class HTMLContentParser(PostParserPlugin):
    """Parses any .html files in a bundle."""

    extensions = ('.html',)

    def parse_post(self, meta, src):
        return src