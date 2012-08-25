from jules.plugins import ContentPlugin


class HTMLContentParser(ContentPlugin):
    """Parses any .rst files in a bundle."""

    extensions = ('.html',)

    def parse(self, content_file):
        src = content_file.read()
        return src

    def parse_string(self, src):
        return src
