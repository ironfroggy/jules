from jules.plugins.post import PostParserPlugin


class HTMLContentParser(PostParserPlugin):
    """Parses any .rst files in a bundle."""

    extensions = ('.html',)

    def parse(self, content_file):
        src = content_file.read()
        return src

    def parse_string(self, src):
        return src