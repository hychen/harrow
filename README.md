# Using Haskell Arrow in Python.

I used to be an adventurer like you but then i took an arrow to the knee....

## Forward pipeline
```
plus1 = lambda n: n + 1
pow2 = lambda n: n * 2
proc = Arrow(plus1).to_a(pow2)

print proc(0) # result: 2
```

## Backward pipeline
```
plus1 = lambda n: n + 1
pow2 = lambda n: n * 2
proc = Arrow(plus1).from_a(pow2)

print proc(0) # result: 0
```

## ArrowChoice

```
arr = Arrow()
proc = Arrow().first()
print proc([1,2,3,4]) # result: 1
proc = Arrow().choice(3)
print proc([1,2,3,4]) # result: 4
```

check test cases for more details...
