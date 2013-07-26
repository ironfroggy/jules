import re

import genshi
from genshi.output import TEXT
from genshi.filters.transform import Transformer, StreamBuffer


from .. import Renderer
from . import MutatingPostProcessingPlugin

#FIXME: make more efficient by having only one MutatingPostProcessingPlugin
#       which converts to genshi and does all the rest of the work, instead of
#       parsing and unparsing for each plugin.

class MutatingPostProcessingHTMLPlugin(MutatingPostProcessingPlugin):
    abstract = True
    input_extension = '.html'
    def process_data(self, data):
        # FIXME: efficiency issue as above.
        stream = genshi.HTML(data)
        stream |= self.process_stream
        
        return stream.render()

class MutatingPostProcessingXMLPlugin(MutatingPostProcessingPlugin):
    abstract = True
    input_extension = '.xml'
    def process_data(self, data):
        # FIXME: efficiency issue as above.
        stream = genshi.XML(data)
        stream |= self.process_stream
        
        return stream.render()

def rewrite_canonical_urls(canon, stream):
    state = "NORMAL"
    for kind, data, pos in stream:
        if kind == 'START':
            element, attrs = data
            if element == "a" and 'href' in attrs:
                href = attrs.get('href')
                m = re.match(r'jules:canon/([^#]*)(#.*)?', href)
                if m is not None:
                    name, frag = m.groups()
                    frag = frag or ''
                    try:
                        url, title = canon[name]
                    except KeyError:
                        # FIXME: log error
                        
                        yield (kind, data, pos)
                        continue
                    
                    attrs |= [('href', url + frag)]
                    yield kind, (element, attrs), pos
                    state = "IN_A"
                    continue
        elif kind == 'END' and state == "IN_A":
            element = data
            if element == "a":
                # yield default content/text
                yield TEXT, title, (None, -1, -1)
        
        yield (kind, data, pos) # I miss goto.
        state = "NORMAL"

class CanonicalUrlRewriter(MutatingPostProcessingHTMLPlugin):
    dependencies = {'renderer': Renderer}
    def process_stream(self, stream):
        return rewrite_canonical_urls(self.renderer.url_canon, stream)
