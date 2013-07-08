import unittest

import sys
import os
import tempfile
import shutil
import subprocess
import textwrap

import jules
from jules import __main__ as main

def run_jules(args):
    subprocess.check_call([sys.executable, "-c", textwrap.dedent("""\
        import sys
        sys.path.insert(0, %r)
        
        from jules import __main__ as m
        m.main(%r)
        """ %
        (os.path.dirname(os.path.abspath(jules.__file__)), ['jules'] + args))])

class TestTemplate(unittest.TestCase):
    """Some basic smoke testing using the `test` template"""
    def test_site(self):
        tempdir = tempfile.mkdtemp(suffix='-jules')
        try:
            projectdir = os.path.join(tempdir, 'test_site')
            
            # create site
            run_jules(['init', projectdir, '-s', 'test'])
            
            # build site
            run_jules(['build', '-L', projectdir])
            
            build = os.path.join(projectdir, '_build')
            
            self.do_test_query(build)
            self.do_test_content(build)
            self.do_test_atall(build)
            self.do_test_static(build)
            self.do_test_rstmeta(build)
            
        finally:
            shutil.rmtree(tempdir)
    
    def do_test_content(self, build):
        p1 = os.path.join(build, 'content', '0', 'index.html')
        p2 = os.path.join(build, 'content', '1', 'index.html')
        ps = os.path.join(build, 'content', 'index.html')
        
        p1 = open(p1).read()
        p2 = open(p2).read()
        ps = open(ps).read()
        
        self.assertTrue("Hello" in p1)
        self.assertTrue("Hello" in p2)
        self.assertTrue('<h1 class="title">Post 1 Title</h1>' in p1)
        self.assertTrue('<h1 class="title">Post 2 Title</h1>' in p2)
        
        link = '<a class="reference external" href="/content/1/">Hubbaloo</a>'
        self.assertTrue(link in p1)
        self.assertTrue(link in p2)
        
        self.assertEqual(ps, "0 1 ")
    
    def do_test_atall(self, build):
        with open(os.path.join(build, 'atall', 'index.html')) as f:
            self.assertEqual(f.read(), 'posts')
        
        with open(os.path.join(build, 'atall', 'post.html')) as f:
            self.assertEqual(f.read(), 'post')
    
    def do_test_query(self, build):
        p1 = os.path.join(build, 'query', '0', 'index.html')
        p2 = os.path.join(build, 'query', '1', 'index.html')
        ps = os.path.join(build, 'query', 'index.html')
        
        p1 = open(p1).read()
        p2 = open(p2).read()
        ps = open(ps).read()
        
        bundlesquery = 'post1_tag post2_tag '
        
        self.assertEqual(p1, bundlesquery)
        self.assertEqual(p2, bundlesquery)
        self.assertEqual(ps, bundlesquery)

    def do_test_static(self, build):
        p1 = open(os.path.join(build, 'static1.txt')).read()
        p2 = open(os.path.join(build, 'static2.txt')).read()
        
        self.assertEqual(p1, 'static file 1')
        self.assertEqual(p2, 'static file 2')
    
    def do_test_rstmeta(self, build):
        p1 = open(os.path.join(build, 'rstmeta', '0', 'index.html')).read()
        p2 = open(os.path.join(build, 'rstmeta', '1', 'index.html')).read()
        
        self.assertEqual(p1, 'Post 1 Title\nPost 1 subtitle')
        self.assertEqual(p2, 'Post 2 Title Override\nPost 2 subtitle override')
