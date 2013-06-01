import unittest

from harrow.arrows import Arrow, map_arr, filter_arr

_plus1 = lambda n: n + 1
_pow2 = lambda n: n * 2
_fn_with_args =  lambda acc, base, base2: acc + base + base2

class ArrowBasicTestCase(unittest.TestCase):

    def test_construnt(self):
        right_prog = Arrow(_plus1).to_a(_pow2)
        self.assertEquals(2, right_prog(0))
        left_prog = Arrow(_plus1).from_a(_pow2)
        self.assertEquals(1, left_prog(0))

    def test_precomputation(self):
        arr = Arrow().map(lambda n: n+1)
        larger2arr = arr.filter(lambda n: n>2)
        self.assertEquals([3,4,5,6,7, 8], larger2arr([1,2,3,4,5,6,7]))

    def test_syntax_sugar(self):
        acc = 1
        arr1 = Arrow(_plus1)
        arr2 = Arrow(_pow2)
        arr3 = arr1 | arr2 
        self.assertEquals(4, arr3(acc))
        arr4 = arr3 | arr1
        self.assertEquals(5, arr4(acc))

    def test_feed(self):
        proc1 = Arrow(map_arr, _plus1).feed([0,0,0,0])
        proc2 = Arrow().from_a(proc1)
        self.assertEquals([1, 1, 1, 1], proc2())

    def test_choice(self):
        arr = Arrow()
        prog = arr.choice(1,  _plus1)
        prog.post(list)
        self.assertEquals([0, 1, 1, 0], prog([0, 0, 1, 0]))
        arr = Arrow()
        prog = arr.choice(1, _fn_with_args, 1, 2)
        prog.post(list)
        self.assertEquals([0, 3, 1, 0], prog([0, 0, 1, 0]))

    def test_parallel(self):
        """***"""
        prog =  Arrow().parallel(lambda n: n+1, lambda n: n+2)
        prog.post(list)
        self.assertEquals([2, 4], prog([1, 2]))
        
    def test_fanout(self):
        """&&&"""
        arr_add1 = Arrow(lambda n: n+1)
        arr_add2 = Arrow(lambda n: n+2)
        arr_add3 = Arrow(lambda n: n+3)
        prog = Arrow().fanout(arr_add1, arr_add2, arr_add3)
        self.assertEquals([2, 3, 4], prog(1))
        prog = Arrow().fanout(t1=arr_add1, t2=arr_add2, t3=arr_add3)
        self.assertEquals({'t1': 2, 't2': 3, 't3': 4}, prog(1))
        
class ChoiceArrowTestCase(unittest.TestCase):

    def test_fanin(self):
        arr_add1 = Arrow(lambda n: n+1).feed(1)
        arr_add2 = Arrow(lambda n: n+2).feed(2)
        arr_add3 = Arrow(lambda n: n+3).feed(3)
        prog = Arrow().fanin(lambda e: e > 3, arr_add1, arr_add2, arr_add3)
        self.assertEquals(4, prog())
        
class ArrowLoopTestCase(unittest.TestCase):

    def test_until(self):
        def append1(lst):
            lst.append(1)
            return lst
            
        proc = Arrow(append1).until(lambda acc: len(acc) == 10)
        self.assertEquals([1, 1, 1, 1, 1, 1, 1, 1, 1, 1], proc([]))
        self.assertEquals([9, 9, 9, 1, 1, 1, 1, 1, 1, 1], proc([9, 9, 9]))
        
    def test_times(self):
        def append_idx(acc):
            (idx, lst) = acc
            lst.append(idx)
            return lst
            
        proc = Arrow(append_idx).times(10)
        self.assertEquals([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11], proc([]))

        proc =  Arrow(append_idx).loop(0, 10, 5)
        self.assertEquals([5, 10, 15], proc([]))

    def test_each(self):
        arr_add1 = lambda acc, a, b: a + b
        proc =  Arrow().each('b', arr_add1, 'fixed: ').post(list).feed(['a', 'b', 'c'])
        self.assertEquals(['fixed: a', 'fixed: b', 'fixed: c'], proc())

