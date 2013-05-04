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

    def test_parallel(self):
        self.assertEquals(5, Arrow().parallel(lambda n: n+1, lambda n: n+2)(1))

    def test_choice(self):
        arr = Arrow()
        prog = arr.choice(_plus1, 1)
        self.assertEquals([0, 1, 0, 0], prog([0, 0, 0, 0]))

    def test_fanout(self):
        arr_add1 = Arrow(lambda n: n+1)
        arr_add2 = Arrow(lambda n: n+2)
        arr_add3 = Arrow(lambda n: n+3)
        prog = Arrow().fanout(arr_add1, arr_add2, arr_add3)
        self.assertEquals([2, 3, 4], prog(1))
