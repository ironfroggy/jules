import unittest

from genshi import HTML

from jules.plugins.rendering.postprocessing import rewrite_canonical_urls

def wrapper(a, b):
    for x in rewrite_canonical_urls(a, b):
        # print "YIELD", x
        yield x

class TestCanonicalUrlRewriter(unittest.TestCase):
    def postprocess(self, html):
        stream = HTML(html)
        stream |= lambda s: wrapper(self.canon, s) # rewrite_canonical_urls(self.canon, s)
        return stream.render('html')
    
    def setUp(self):
        self.canon = {'url1': ('/url1.html', u"URL 1")}
    
    def test_leaves_alone(self):
        html = u'<a href="foo"></a>'
        self.assertEqual(
            self.postprocess(html),
            html)
    
    def test_postprocess_keeptitle(self):
        self.assertEqual(
            self.postprocess(u'<a href="jules:canon/url1">my url</a>'),
            u'<a href="/url1.html">my url</a>')
    
    def test_postprocess_newtitle(self):
        self.assertEqual(
            self.postprocess(u'<a href="jules:canon/url1"></a>'),
            u'<a href="/url1.html">URL 1</a>')
        self.assertEqual(
            self.postprocess(u'<a href="jules:canon/url1"/>'),
            u'<a href="/url1.html">URL 1</a>')
    
    def test_postprocess_nested(self):
        html = u'<a href="jules:canon/url1"><a href="jules:canon/url1"/></a>'
        self.assertEqual(
            self.postprocess(html),
            '<a href="/url1.html"><a href="/url1.html">URL 1</a></a>')

    def test_postprocess_keepfragment(self):
        self.assertEqual(
            self.postprocess(u'<a href="jules:canon/url1#frag">my url</a>'),
            u'<a href="/url1.html#frag">my url</a>')