import unittest

from jules.plugins.post import rst

class TestUpdateMeta(unittest.TestCase):
    def test_null_update(self):
        m = {}
        rst.update_meta(m, {})
        self.assertEqual(m, {})

    def test_lhs_update(self):
        m = {1: 2}
        rst.update_meta(m, {})
        self.assertEqual(m, {1: 2})

    def test_atomic_update(self):
        m = {1: 2}
        rst.update_meta(m, {2: 3})
        self.assertEqual(m, {1: 2, 2: 3})

    def test_atomic_overwrite(self):
        m = {1: 2}
        rst.update_meta(m, {1: 3})
        self.assertEqual(m, {1: 3})

    def test_seq_update(self):
        m = {1: 2}
        rst.update_meta(m, {2: [0]})
        self.assertEqual(m, {1: 2, 2: [0]})

    def test_seq_overwrite(self):
        m = {1: 2}
        rst.update_meta(m, {1: [0]})
        self.assertEqual(m, {1: [0]})

    def test_seq_append(self):
        m = {1: [0]}
        rst.update_meta(m, {1: [2]})
        self.assertEqual(m, {1: [0, 2]})
    
    def test_map_update(self):
        m = {1: 2}
        rst.update_meta(m, {2: {3:4}})
        self.assertEqual(m, {1: 2, 2: {3:4}})

    def test_map_overwrite(self):
        m = {1: 2}
        rst.update_meta(m, {1: {2: 3}})
        self.assertEqual(m, {1: {2: 3}})

    def test_map_recurse(self):
        m = {1: {2:3}}
        rst.update_meta(m, {1: {3:4}})
        self.assertEqual(m, {1: {2:3, 3:4}})

    def test_rhs_overwriting(self):
        m = {1: {}, 2: []}
        rst.update_meta(m, {1: 2, 2: 3})
        self.assertEqual(m, {1: 2, 2: 3})
