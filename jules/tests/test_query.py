import unittest

import jules
from jules.query import *

class Namespace(object):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __repr__(self):
        return '<Namespace %r>' % (self.__dict__,)

def Val(x): return Namespace(**val(x))
class Val(object):
    def __init__(self, *args, **kwargs):
        self.components = val(*args, **kwargs)
def val(x): return dict(val=x)

config = dict(templates=[])

class TestSimpleQuery(unittest.TestCase):
    bundle = Val(1)
    e = QueryEngine(config, jules.PluginEngine())
    rs = ResultSet(e, [bundle])
    
    def test_no_results(self):
        self.assertEqual(
            list(self.rs.select(forbid_components=['val'])),
            [])
    
    def test_null_result(self):
        self.assertEqual(
            list(self.rs.select()),
            [{}])
    
    def test_simple(self):
        self.assertEqual(
            list(self.rs.select(require_components=['val'])),
            [val(1)])
    
    def test_where(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .where(['True'])),
            [val(1)])
        
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .where(['True', 'False'])),
            [])
    
    def test_rename_none(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .rename({})),
            [{}])
    
    def test_rename(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .rename({'k1': 'val', 'k2': 'val'})),
            [dict(k1=1, k2=1)])

class Test2Query(unittest.TestCase):
    bundle1 = Val(1)
    bundle2 = Val(2)
    e = QueryEngine(config, jules.PluginEngine())
    rs = ResultSet(e, [bundle1, bundle2])

    def test_default_sort(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .order_by(key='val')),
            [val(1), val(2)])
    
    def test_asc_sort(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .order_by(key='val', descending=False)),
            [val(1), val(2)])
    
    def test_desc_sort(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .order_by(key='val', descending=True)),
            [val(2), val(1)])

    def test_limit(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .limit(1)),
            [val(1)])

    def test_count(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .order_by(key='val', descending=False)
                .count('val')),
            [val(0), val(1)])

class TestGroupBy(unittest.TestCase):
    bundle1 = Val((1,))
    bundle2 = Val((2,))
    bundle3 = Val((1, 2,))
    bundle4 = Val((1,))
    e = QueryEngine(config, jules.PluginEngine())
    rs = ResultSet(e, [bundle1, bundle2, bundle3, bundle4])
    
    def test_group_by_eq(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .group_by_eq('val')),
            [dict(key=(1,), group=[val((1,)), val((1,))]),
             dict(key=(2,), group=[val((2,))]),
             dict(key=(1, 2), group=[val((1, 2))])])
    
    def test_group_by_in(self):
        self.assertEqual(
            list(self.rs
                .select(require_components=['val'])
                .group_by_in('val')),
            [dict(key=1, group=[val((1,)), val((1, 2)), val((1,))]),
             dict(key=2, group=[val((2,)), val((1, 2))])])
