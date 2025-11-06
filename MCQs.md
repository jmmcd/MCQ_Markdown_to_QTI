1. How does Scikit-Learn know that an Estimator has not yet been fitted?

* The `predict()` method does not yet exist
* The prediction is always 0
* The train performance is bad
* The test performance is bad
+ Some other way


2. Which one of these is correct, assuming we want a `defaultdict` where the default is `0`?

* `d = defaultdict(0)`
* `d = defaultdict(int)`
+ `d = defaultdict(lambda: int)`
* None of the above

3. What result do we get from this code?
```
A = np.zeros((3, 2))
B = np.ones(3)
C = A + B
```

* `C` has shape `(3, 2)`
* `C` has shape `(2, 3)`
* `C` has shape `(2,)`
* `C` has shape `(3,)`
* `C` has shape `(3, 2, 3)`
* `C` has shape `(3, 6)`
* `ValueError`


4. Which are correct? Select zero, one, or more.

* In Python, the floating-point system gives more small rounding errors than in Java, C or other languages
* In Python, when using the `==` operator with `float`s, if the left- and right-hand sides are close but not identical, the operator still returns True 
* In Python, the smallest number that can be represented by a `float` is known as machine epsilon, approximately `10**-6`
+ In Python, the difference between a `float` `x` and the next larger `float` `y` is a small number that depends on the value of `x`.


5. What result do we get from `itertools.combinations('ABCD', r=2)`?

* A `list` of 2 items
* A generator that will `yield` 2 items
* A `list` of 6 items
+ A generator that will `yield` 6 items
* An error


6. What is the result of `np.array([1, 2, 3]) > 2`?

+ `array([False, False, True])`
* `[False, False, True]`
* `True`
* `1`


7. What is the result of `[] + []`?

+ `[]`
* `[[]]`
* An error
* `None`


8. Which of these is an example of canonicalisation?

* When a person becomes a saint
* When an algorithm is proved to be optimal for a given problem, and it is added to the standard library+
+ When we convert all input strings to a lower-case form and remove all punctuation before further processing
* When we scale all input values to the range `[0, 1]`
* None of the above


9. What is `{1, 2, 3} & {2, 3, 4}`?

* `{2, 3}`
+ `{1, 2, 3, 4}`
* `{1, 4}`
* `TypeError`







