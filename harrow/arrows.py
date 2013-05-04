import copy

def dup(acc):
    newacc = copy.copy(acc)
    return [acc, newacc]

def choice(acc, i):
    return acc[i]

def fanout_arrs(acc, arrs):
    return [arr(acc) for arr in arrs]

def parallel_arrs(acc, arrs):
    hd = arrs[0]
    tl = arrs[1:]
    ret = hd(acc)
    for arr in tl:
        ret += arr(acc)
    return ret

def map_arr(acc, f):
    return map(f, acc)

def filter_arr(acc, f):
    return filter(f, acc)

class _BaseArrow(object):

    def __init__(self, *args, **kwargs):
        self.funcs = []
        self.acc = None

        if args:
            fn = args[0]
            args = args[1:]
            self.post(fn, *args, **kwargs)

    def __call__(self, acc=None):
        if acc is None:
            ret = self.acc
        else:
            ret = acc
        for (fn, args, kwargs) in self.funcs:
            ret = fn(ret, *args, **kwargs)
        return ret

    def __or__(self, arr):
        return self.to_a(arr)

    def thunk(self, acc):
        return lambda : self(acc)

    def pre(self, fn, *args, **kwargs):
        self.funcs.insert(0, (fn, args, kwargs))
        return self

    def post(self, fn, *args, **kwargs):
        self.funcs.append((fn, args, kwargs))
        return self

    def copy(self):
        return self.__class__(self)

    def to_a(self, arr):
        """
        >>> add1 = lambda n : n + 1
        >>> arr = Arrow(add1).to_a(Arrow(add1))
        >>> arr(0)
        2
        """
        new = self.copy()
        new.post(arr)
        return new

    def from_a(self, arr):
        new = self.copy()
        new.pre(arr)
        return new

    def parallel(self, *arrs):
        new = self.copy()
        new.post(parallel_arrs, arrs)
        return new

class ArrowChoice(object):

    def split(self, arr):
        new = self.copy()
        new.post(dup)
        return new.to_a(arr)

    def choice(self, i):
        new = self.copy()
        new.post(choice, i)
        return new

    def first(self):
        return self.choice(0)

    def second(self):
        return self.choice(1)

    def fanout(self, *arrs):
        new = self.copy()
        new.pre(fanout_arrs, arrs)
        return new

# @TODO: provide a plugin hook.
Arrow = type('Arrow', (_BaseArrow, ArrowChoice), {})
