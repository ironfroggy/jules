import re

from docutils.core import publish_parts
from docutils import nodes, utils
from docutils.parsers.rst import roles

from jules.plugins.post import PostParserPlugin
from jules.plugins.rendering import Renderer

class RstContentParser(PostParserPlugin):
    """Parses any .rst files in a bundle."""

    dependencies = (Renderer,)
    extensions = ('.rst',)
    
    def __init__(self, f, engine, renderer):
        super(RstContentParser, self).__init__(f, engine)
        self.renderer = renderer
    
    def parse_string(self, src):
        parts = publish_parts(source=src, writer_name='html',
            settings_overrides={'url_canon': self.renderer.url_canon})
        return parts['html_body']


def doclink(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Link to another document.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages. Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """

    try:
        m = re.match(r'(.*)<([-\w]+)(#[-\w]+)?>', text)
        label, key, anchor = m.groups()
    except (AttributeError, re.error):
        label = None
        key = text
    try:
        url, title = inliner.document.settings.url_canon[key]
    except KeyError:
        raise ValueError(
            "Cannot render a doclink for directive %s, "
            "because there is no canonical URL for %r" % (rawtext, key))

    # FIXME: this creates an external reference. Need to make internal (how?)
    # FIXME: anchor is ignored
    node = nodes.reference(
        rawtext,
        utils.unescape(label or title),
        refuri=url,
        **options)

    return [node], []

roles.register_canonical_role('doclink', doclink)