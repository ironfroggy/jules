from jules.plugins import ContentPlugin

from docutils.core import publish_parts


class RstContentParser(ContentPlugin):
    """Parses any .rst files in a bundle."""

    extensions = ('.rst',)
    
    def parse(self, content_file):
        src = content_file.read()
        return self.parse_string(src)

    def parse_string(self, src):
        parts = publish_parts(source=src, writer_name='html')
        return parts['html_body']
