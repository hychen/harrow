import operator

def choice(acc, i, arr, *args, **kwargs):
    for idx, e in enumerate(acc):
        if idx == i:
            yield arr(e, *args, **kwargs)
        else:
            yield e
            
def fanout_arrs(acc, arrs=None, kwarrs=None):
    if arrs:
        return [arr(acc) for arr in arrs]
    elif kwarrs:
        return {tag: arr(acc) for tag, arr in kwarrs.items()}
    else:
        raise Exception('no input arrows')

def parallel_arrs(acc, arrs):
    assert len(acc) == len(arrs)
    for idx,e in enumerate(acc):
        yield arrs[idx](acc[idx])
    
def map_arr(acc, f, *args, **kwargs):
    return map(f, acc, *args, **kwargs)

def filter_arr(acc, f, *args, **kwargs):
    return filter(f, acc, *args, **kwargs)

def times_arr(acc, i, arr, *args, **kwargs):
    """Repeate function

    Args:
    - i:
    - arr: function
    Returns:
    - Arrow
    """
    for idx in range(0, i):
        yield arr(idx, acc, *args, **kwargs)

def thunk(f, *args, **kwargs):

    """Defer evaluation of an Arrow.

    Returns:
    - 0-args lambda function.
    """
    return lambda: f(*args, **kwargs)
    
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

    def map(self, *args, **kwargs):
        """Return a list of the results of applying the function to the items of acc

        Args:
        - fn: function that the first argument is acc
        - *args: reset arguments of function 
        - **kwargs: keyword arguments of function
        Returns:
        - Arrow
        """
        self.post(map_arr, *args, **kwargs)
        return self
        
    def filter(self, *args, **kwargs):
        """Return those items of sequence for which function(item) is true.
        
        Args:
        - fn: function that the first argument is acc
        - *args: reset arguments of function 
        - **kwargs: keyword arguments of function
        Returns:
        - Arrow
        """
        self.post(filter_arr, *args, **kwargs)
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

    def choice_apply(self, i, arr, *args, **kwargs):
        """Send the nth component of the input through the argument arrow, and copy the rest unchanged to the output.
        """
        new = self.copy()
        new.post(choice, i, arr, *args, **kwargs)
        return new

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

    def fanout(self, *arrs, **kwarrs):
        """Fanout: send the input to both argument arrows and combine their output.

        Args:
        - *arrs: list of Arrows.
        Returns:
        - Arrow
        """
        new = self.copy()
        new.pre(fanout_arrs, arrs, kwarrs)
        return new

def multiplex(acc, tags):
    ret = None
    for i, tag in enumerate(tags):
        if ret is None:
            ret = [0 for _ in range(0, len(tags))] if type(tag) is int else {}
        ret[tag] = acc[i]
    return ret
    
class ArrowChoice(object):

    def choice(self, tag):
        """get an output result of input arrows by tag
        """    
        self.post(lambda acc: acc[tag])
        return self
    
    def select(self, *tags):
        """get an output results of input arrows by tags. 
        """
        self.post(lambda acc: [acc[tag] for tag in tags])
        return self

    def multiplex(self, *tags):
        self.post(multiplex,  tags)
        return self
    
    def fanin(self, f=operator.add):
        """merge their outputs of arrows.

        Args:
        - f: merge function.
        Returns:
        - Arrow
        """
        #@FIXME: roundant codes here. 
        self.post(lambda acc: reduce(lambda ret, xs: f(ret, xs), acc))
        return self

def each_arr(acc, k, arr, *args, **kwargs):
    for v in acc:
        kwargs[k] = v
        yield arr(acc, *args,**kwargs)

def until_arr(acc, input_f, feadback_f):
    cur_result = input_f(acc)
    done = feadback_f(cur_result)
    
    if done:
        return cur_result
    else:
        return until_arr(cur_result, input_f, feadback_f)

def trace_arr(acc, input_f, feadback_f, feadback_acc):
    (done, next_fd_acc) =  feadback_f(feadback_acc, acc)
    cur_result = input_f((next_fd_acc, acc))
    if done:
        return cur_result
    else:
        return trace_arr(cur_result, input_f, feadback_f, next_fd_acc)
        
class ArrowLoop(object):

    def until(self, fd):
        """
        Args:
        - fd: a function to check the product value. 
        """
        return Arrow(until_arr, self, fd)
        
    def trace(self, fd, fd_acc = None):
        return Arrow(trace_arr, self, fd, fd_acc)
        
    def times(self, i):
        return self.loop(0, i, 1)
        
    def loop(self, start, end, step):
        return self.trace(lambda idx, acc: (idx == end, step + idx), start)

    def each(self, k, f,*args,**kwargs):
        new = self.copy()
        new.post(each_arr, k, f, *args,**kwargs)
        return new

# @TODO: provide a plugin hook.
Arrow = type('Arrow', (_BaseArrow, ArrowChoice,  ArrowLoop), {})
