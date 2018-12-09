"""
.. automodule:: fdl
   :members:
   :platform: Windows
   :synopsis: Utilities for functional programming in Python.
.. moduleauthor:: EventHelix.com Inc.
"""

from typing import TypeVar, Generic, NamedTuple, Iterable


a = TypeVar('a')


class Maybe(NamedTuple('Maybe', [('hasValue', bool) , ('value', a)]), Generic[a]):
    """
    A container of 0 or 1 element.
    """ 
    def __repr__(self) -> str :
        """
        Returns a printable string for the Maybe class.
        """ 
        if self.hasValue:
            return f'just({repr(self.value)})'
        else: 
            return 'nothing()'

    def map(self, f) :
        """
        Applies the given function to the contained value if it is present.
        This follows the law,
        xs.map(f).map(g) ≡ xs.map(compose(f, g))
        , when f and g are pure functions
        """ 
        if self.hasValue:
            return just(f(self.value))
        else: return nothing()

    def do(self, f):
        """
        Facilitate function chaining in Maybe.
        """
        if self.hasValue :
            f(self.value)
            return self
        else : return self
    # (xs >>= f) >>= g ≡ x >>= \ x -> f(x) >>= g
    def then(self, f) :
        """
        Chain potentially failing computations without a nested if statement.
        xs.then(just) ≡ xs
        xs.then(lambda x: f(x).then(g)) ≡ xs.then(g).then(g)
        where f and g are pure functions
        """
        if self.hasValue :
            return f(self.value)
        else : nothing()

def nothing() -> Maybe[a] :
    """
    Construct and empty Maybe.
    """
    return Maybe(False, None)

def just(x : a) -> Maybe[a] :
    """
    Construct a Maybe with value
    """
    return Maybe(True, x)

def first(xs : Iterable[a], condition = lambda x: True) -> Maybe[a]:
    """
    Returns the first item in the `iterable` that
    satisfies the `condition`.

    If the condition is not given, returns the first item of
    the iterable.

    Raises `StopIteration` if no item satysfing the condition is found.

    >>> first( (1,2,3), condition=lambda x: x % 2 == 0)
    2
    >>> first(range(3, 100))
    3
    >>> first( () )
    Traceback (most recent call last):
    ...
    StopIteration
    """
    try:
        return just(next(x for x in xs if condition(x)))
    except StopIteration:
        return nothing()

