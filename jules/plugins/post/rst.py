import re

from docutils.core import publish_parts
from docutils import nodes, utils
from docutils.parsers.rst import roles, directives, Directive

import yaml

from jules.plugins.post import PostParserPlugin
from jules.plugins.rendering import Renderer

class RstContentParser(PostParserPlugin):
    """Parses any .rst files in a bundle."""
    extensions = ('.rst',)
    
    def parse_post(self, meta, src):
        parts = publish_parts(source=src, writer_name='html',
            settings_overrides={
                'meta': meta
        })
        
        meta.setdefault('title', parts['title'])
        meta.setdefault('subtitle', parts['subtitle'])
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
        anchor = None
        key = text

    # FIXME: this creates an external reference. Need to make internal (how?)
    node = nodes.reference(
        rawtext,
        utils.unescape(label or ''),
        refuri="jules:canon/" + key + ("#" + anchor if anchor else ''),
        **options)

    return [node], []

roles.register_canonical_role('doclink', doclink)

class JulesMeta(Directive):

    required_arguments = 0
    optional_arguments = 0
    has_content = True

    def run(self):
        try:
            d = yaml.load('\n'.join(self.content))
        except yaml.parser.ParserError:
            raise ValueError("Invalid YAML data")

        # docutils is stupid.
        meta = self.state_machine.document.settings.meta
        update_meta(meta, d)

        return []

directives.register_directive("jules", JulesMeta)

def update_meta(meta, update):
    for k, v in update.iteritems():
        if k in meta:
            if isinstance(v, list) and isinstance(meta[k], list):
                meta[k].extend(v)
                continue
            elif isinstance(v, dict) and isinstance(meta[k], dict):
                update_meta(meta[k], v)
                continue
        # else (for all of them) (thank goodness we don't need goto here)
        meta[k] = v
    
