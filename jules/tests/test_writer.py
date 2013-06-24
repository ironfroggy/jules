import unittest

from jules import writer

class TestNormalize(unittest.TestCase):
    def test_already(self):
        p = '/foo/bar'
        self.assertEqual(writer.URLWriter.normalize_url(p), p)
    
    def test_dir(self):
        p = '/foo/bar/'
        self.assertEqual(
            writer.URLWriter.normalize_url(p),
            '/foo/bar/index.html')
    
    def test_doubleslash(self):
        p = '/foo//bar'
        self.assertEqual(writer.URLWriter.normalize_url(p), p)

class TestSplit(unittest.TestCase):
    def test_null(self):
        self.assertEqual(writer.URLWriter.split_url('/'), ())

    def test_singleton(self):
        self.assertEqual(writer.URLWriter.split_url('/a'), ('a',))

    def test_three(self):
        self.assertEqual(writer.URLWriter.split_url('/a/b/c'), tuple('abc'))

    def test_unnormalized(self):
        self.assertEqual(writer.URLWriter.split_url('/a/'), ('a', ''))
    
    def test_rel(self):
        self.assertRaises(ValueError, writer.URLWriter.split_url, 'a/b')