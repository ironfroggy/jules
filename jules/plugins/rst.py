from jules.plugins import ContentPlugin

from docutils.core import publish_parts


class RstContentParser(ContentPlugin):
    """Parses any .rst files in a bundle."""

    extensions = ('.rst',)
    
    def parse(self, content_file):
        src = content_file.read()
        parts = publish_parts(source=src, writer_name='html')
        return parts['html_body']
