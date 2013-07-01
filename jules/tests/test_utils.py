import unittest

import jules
from jules import utils

class TestMerge(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(
            utils.merge({}, {}),
            {})

    def test_left(self):
        self.assertEqual(
            utils.merge({'a': 1}, {}),
            {'a': 1})

    def test_right(self):
        self.assertEqual(
            utils.merge({}, {'a': 1}),
            {'a': 1})

    def test_disjoint(self):
        a = {'a': 1}
        b = {'b': 2}

        self.assertEqual(
            utils.merge(a, b),
            {'a': 1, 'b': 2})
        
        self.assertEqual(a, {'a': 1})
        self.assertEqual(b, {'b': 2})

    def test_nondisjoint(self):
        self.assertRaises(
            utils.KeyConflictError,
            utils.merge,
                {'a': 1},
                {'a': 1})
    
