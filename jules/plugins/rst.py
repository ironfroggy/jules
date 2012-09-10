import re

from jules.plugins import ContentPlugin

from docutils.core import publish_parts
from docutils import nodes, utils
from docutils.parsers.rst import roles


class RstContentParser(ContentPlugin):
    """Parses any .rst files in a bundle."""

    extensions = ('.rst',)
    
    def parse_string(self, src):
        parts = publish_parts(source=src, writer_name='html',
            settings_overrides={'jules': self.engine})
        return parts['html_body']


def doclink(name, rawtext, text, lineno, inliner, options={}, content=[]):
    """Link to another document.

    Returns 2 part tuple containing list of nodes to insert into the
    document and a list of system messages.  Both are allowed to be
    empty.

    :param name: The role name used in the document.
    :param rawtext: The entire markup snippet, with role.
    :param text: The text marked with the role.
    :param lineno: The line number where rawtext appears in the input.
    :param inliner: The inliner instance that called us.
    :param options: Directive options for customization.
    :param content: The directive content for customization.
    """

    engine = inliner.document.settings.jules
    try:
        m = re.match(r'(.*)<([-\w]+)>', text)
        label, key = m.groups()
    except (AttributeError, re.error):
        label = None
        key = text
    try:
        bundle = engine.get_bundle(key=key)
        assert bundle.url() is not None
    except (ValueError, AssertionError):
        raise ValueError("Cannot render a doclink for directive %s, becuase there is no bundle %r" % (rawtext, key))
    node = make_link_node(rawtext, label, bundle, options)

    return [node], []


def make_link_node(rawtext, label, bundle, options):
    """Create a link to a BitBucket resource.

    :param rawtext: Text being replaced with link node.
    :param type: Link type (issue, changeset, etc.)
    :param slug: ID of the thing to link to
    :param options: Options dictionary passed to role func.
    """
    ref = bundle.url()
    title = bundle.meta.get('title', bundle.key)
    node = nodes.reference(rawtext, utils.unescape(label or title), refuri=ref,
                           **options)
    return node

roles.register_canonical_role('doclink', doclink)
