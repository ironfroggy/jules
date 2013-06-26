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
            
            # FIXME: test output
            #        currently there is no output, so this test case just makes
            #        sure nothing throws an exception. That isn't too useful!
        finally:
            shutil.rmtree(tempdir)
