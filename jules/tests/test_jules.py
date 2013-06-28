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
            
            p1 = os.path.join(projectdir, '_build', 'posts', '0', 'index.html')
            p2 = os.path.join(projectdir, '_build', 'posts', '1', 'index.html')
            ps = os.path.join(projectdir, '_build', 'posts', 'index.html')
            
            p1 = open(p1).read()
            p2 = open(p2).read()
            ps = open(ps).read()
            
            bundlesquery = 'post1_tag post2_tag '
            
            self.assertTrue(p1.startswith(bundlesquery))
            self.assertTrue(p2.startswith(bundlesquery))
            self.assertTrue("Hello" in p1)
            self.assertTrue("Hello" in p2)
            self.assertTrue('<h1 class="title">Post 1 Title</h1>' in p1)
            self.assertTrue('<h1 class="title">Post 2 Title</h1>' in p2)
            self.assertEqual(ps, "0 1 \n" + bundlesquery)
        finally:
            shutil.rmtree(tempdir)
