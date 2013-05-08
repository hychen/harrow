# Using Haskell Arrow in Python.

I used to be an adventurer like you but then i took an arrow to the knee....

## Forward pipeline

```
from harrow import arr
plus1 = lambda n: n + 1
pow2 = lambda n: n * 2
# pow2(plus1(0))
proc = arr(plus1).to_a(pow2)
print proc(0) # result: 2
# syntax sugar
proc = arr(plus1) | arr(plus2)
print proc(0) # result: 2
```

## Backward pipeline
```
from harrow import arr
plus1 = lambda n: n + 1
pow2 = lambda n: n * 2
# plus1(pow2(0))
proc = arr(plus1).from_a(pow2)
print proc(0) # result: 1
```

## syntax sugar of forward pipeline

```
proc = Arrow(lambda n:n+1) | Arrow(lambda n:n+2)
print proc(1)

```

## Feed 

The input argument of a arrow or a pipeline can predefined by feed method.

```
from harrow import arr
from harrow.arrows import Arrow
# set acc
proc = arr().feed(1)
proc.post(lambda acc: acc+1)
print proc()
# the result is 2
# ------------------------------------------------------
proc2 = Arrow(lambda n:n+1).to_a(Arrow(lambda n:n+2))
proc2.feed(3)
print proc()
# the result is 6
```

## Choice

Send the nth component of the input through the argument arrow, and copy the rest unchanged to the output.

```
from harrow import arr
arr1 = arr()
proc = arr1.choice(1, lambda n: n + 1)
print proc([1,2,3,4]) # result: [1, 3, 3, 4])
```

## Fanout

send the input to both argument arrows and combine their output.

```
>>> from harrow import arr
>>> import urllib
>>> gpage = arr(urllib.urlopen, "http://www.google.com")
>>> ypage = arr(urllib.urlopen, "http://www.yahoo.com")
>>> prog = arr().fanout(gpage, ypage)
# put all output of arrows into a list.
>>> print prog()
[<addinfourl at 140422088441440 whose fp = <socket._fileobject object at 0x7fb692c21150>>, <addinfourl at 140422122947576 whose fp = <socket._fileobject object at 0x7fb692c1b750>>]
```

## Fanin

Split the input between the argument arrows and combine their output.

```
# construct 3 arrows.
arr_add1 = Arrow(lambda n: n+1).feed(1)
arr_add2 = Arrow(lambda n: n+2).feed(2)
arr_add3 = Arrow(lambda n: n+3).feed(3)
# construct a arrow that find first number in input is bigger than 3.
prog = Arrow().fanin(lambda e: e > 3, arr_add1, arr_add2, arr_add3)
# the result is 4.
```

## Parallel

Split the input between the two argument arrows and combine their output.

```
f = lambda n: n+1
g = lambda n: n+2
prog =  arr().parallel(f,g)
prog.post(list)
# compute f(1) and g(1) and combine the result.
print prog([1,2])
``
