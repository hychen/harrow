# Using Haskell Arrow in Python.

I used to be an adventurer like you but then i took an arrow to the knee....

## Forward pipeline

```
plus1 = lambda n: n + 1
pow2 = lambda n: n * 2
# pow2(plus1(0))
proc = Arrow(plus1).to_a(pow2)
print proc(0) # result: 2

# syntax sugar
proc = Arrow(plus1) | Arrow(plus2)
print proc(0) # result: 2
```

## Backward pipeline
```
plus1 = lambda n: n + 1
pow2 = lambda n: n * 2
# plus1(pow2(0))
proc = Arrow(plus1).from_a(pow2)

print proc(0) # result: 1
```

## ArrowChoice

```
arr = Arrow()
proc = arr.choice(lambda n: n + 1, 0)
print proc([1,2,3,4]) # result: [2, 2, 3, 4])
```

check test cases for more details...
