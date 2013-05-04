import unittest

from harrow.arrows import Arrow, map_arr, filter_arr

_plus1 = lambda n: n + 1
_pow2 = lambda n: n * 2

class ArrowBasicTestCase(unittest.TestCase):

    def test_construnt(self):
        right_prog = Arrow(_plus1).to_a(_pow2)
        self.assertEquals(2, right_prog(0))
        left_prog = Arrow(_plus1).from_a(_pow2)
        self.assertEquals(1, left_prog(0))

    def test_precomputation(self):
        arr = Arrow(map_arr, lambda n: n+1)
        larger2arr = arr.post(filter_arr, lambda n: n>2)
        self.assertEquals([3,4,5,6,7, 8], larger2arr([1,2,3,4,5,6,7]))

    def test_syntax_sugar(self):
        acc = 1
        arr1 = Arrow(_plus1)
        arr2 = Arrow(_pow2)
        arr3 = arr1 | arr2 
        self.assertEquals(4, arr3(acc))
        arr4 = arr3 | arr1
        self.assertEquals(5, arr4(acc))

class ChoiceArrowTestCase(unittest.TestCase):

    def test_split_and_choice(self):
        acc = 0 
        prog = Arrow(lambda acc: acc + 1).split(Arrow(lambda acc: [acc[0], acc[1]+1]))
        self.assertEquals([1, 2], prog(acc))
        prog1 = prog.first()
        self.assertEquals(1, prog1(acc))
        prog2 = prog.second()
        self.assertEquals(2, prog2(acc))

    def test_fanout(self):
        _add = lambda n : n + 1
        a1 = Arrow(_add).thunk(0)
        a2 = Arrow(_add).thunk(1)
        a3 = Arrow(_add).thunk(2)
        prog = Arrow().fanout(a1, a2, a3)
        self.assertEquals(['o', 1, 2, 3], prog('o'))
        self.assertEquals('o', prog.first()('o'))
