
def choice(acc, i, arr, *args, **kwargs):
    for idx, e in enumerate(acc):
        if idx == i:
            yield arr(e, *args, **kwargs)
        else:
            yield e

def fanout_arrs(acc, arrs):
    return [arr(acc) for arr in arrs]

def parallel_arrs(acc, arrs):
    assert len(acc) == len(arrs)
    for idx,e in enumerate(acc):
        yield arrs[idx](acc[idx])
    
def map_arr(acc, f):
    return map(f, acc)

def filter_arr(acc, f):
    return filter(f, acc)
    
# --------------------------------------------------------- 
# Classes
# --------------------------------------------------------- 
class _BaseArrow(object):

    def __init__(self, *args, **kwargs):
        """

        Args:
        - f: callable functions
        - *args: arguments of callable object.
        - **kwargs: keyword argyments of callable object.
        """
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
        """syntax sugar of right to left composition.
        """
        return self.to_a(arr)

    # --------------------------------------------------------- 
    # Public Methods
    # --------------------------------------------------------- 
    def feed(self, acc):
        """Setup accumulator of an Arrow.

        Args:
        - acc: accumulator of fold operation.
        Returns:
        - Self
        """
        self.acc = acc
        return self

    def thunk(self):
        """Defer evaluation of an Arrow.

        Returns:
        - 0-args lambda function.
        """
        return lambda acc: self(acc)

    def pre(self, fn, *args, **kwargs):
        """Precomposition with a pure function.

        Args:
        -  fn: callable object.
        - *args: arguments of fn
        - **kwargs:  arguments of fn
        Returns:
        - Self
        """
        self.funcs.insert(0, (fn, args, kwargs))
        return self

    def post(self, fn, *args, **kwargs):
        """Postcomposition with a pure function.

        Args:
        -  fn: callable object.
        - *args: arguments of fn
        - **kwargs:  arguments of fn
        Retuns:
        - Self
        """
        self.funcs.append((fn, args, kwargs))
        return self

    def copy(self):
        """Creatre a new Arrow contains self.

        Returns:
        - Arrow
        """
        return self.__class__(self)

    def to_a(self, arr):
        """Left to right composition

        Args:
        - arr: Arrow

        Returns:
        - Arrow       
        """
        new = self.copy()
        new.post(arr)
        return new

    def from_a(self, arr):
        """Right to left composition

        Args:
        - arr: Arrow

        Returns:
        - Arrow        
        """        
        new = self.copy()
        new.pre(arr)
        return new

    def choice(self, i, arr, *args, **kwargs):
        """Send the nth component of the input through the argument arrow, and copy the rest unchanged to the output.
        """
        new = self.copy()
        new.post(choice, i, arr, *args, **kwargs)
        return new

    def first(self, arr, *args, **kwargs):
        """Send the first component of the input through the argument arrow, and copy the rest unchanged to the output.

        Args:
        - arr: callable object.

        Returns:
        - Arrow
        """
        return self.choice(0, arr, *args, **kwargs)

    def parallel(self, *fs, **opts):
        """Split the input between the two argument arrows and combine their output.

        Args:
        - *fs: a list of callable objects.
        - lazy: true
        Returns:
        - Arrow
        """
        new = self.copy()
        new.post(parallel_arrs, fs)
        return new

class ArrowChoice(object):

    def second(self, arr, *args, **kwargs):
        """
        """
        return self.choice(1, arr, *args, **kwargs)

    def fanout(self, *arrs):
        new = self.copy()
        new.pre(fanout_arrs, arrs)
        return new

# @TODO: provide a plugin hook.
Arrow = type('Arrow', (_BaseArrow, ArrowChoice), {})
