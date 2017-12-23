from typing import TypeVar, Generic, NamedTuple, Iterable


a = TypeVar('a')


class Maybe(NamedTuple, Generic[a]): # ('Maybe', [('hasValue', bool) , ('value', a)])
    hasValue : bool
    value : a
    def __repr__(self) -> str : 
        if self.hasValue:
            return f'just({repr(self.value)})'
        else: 
            return 'nothing()'
    def map(self, f) :
        if self.hasValue:
            return just(f(self.value))
        else: return nothing()

def nothing() -> Maybe[a] : return Maybe(False, None)
def just(x : a) -> Maybe[a] : return Maybe(True, x)



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

