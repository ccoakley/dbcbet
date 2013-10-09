
"""
Helpers for reusable contract components.

Now that we have preconditions, postconditions, and invariants, let us provide some abstractions:
1. a "returns" predicate. This is a postcondition that tests the return value.
2. an "args" predicate. This tests the parameters with additional predicates.
3. an "immutable" predicate. This tests for immutability of self (old==self).

Since some of those take additional predicates, some abstractions might be nice:
1. nullable: allows null (or an additional test, passed in, such as nullable(positive)
2. numeric tests: (number, positive, negative)
3. logical tests: (not, and, or) with negative==not(positive), nonzero==or(positive, negative)
4. is_type: some kind of isinstance wrapper
"""
from functools import wraps

def returns(predicate):
    """DBC helper for reusable, simple predicates for return-value tests used in postconditions"""
    @wraps(predicate)
    def return_wrapped(s, old, ret, *args, **kwargs):
        return predicate(ret)
    return return_wrapped    

def state(predicate):
    """DBC helper for reusable, simple predicates for object-state tests used in both preconditions and postconditions"""
    @wraps(predicate)
    def wrapped_predicate(s, *args, **kwargs):
        return predicate(s)
    return wrapped_predicate

def args(*arglist):
    """DBC helper for reusable, simple predicates for argument-value tests used in preconditions"""
    @wraps(predicate)
    def positional_predicate(s, *ar, **kw):
        for pred, arg in zip(arglist, ar):
            if not pred(ar):
                return False
        return True
    return positional_predicate

def _not(predicate):    
    """DBC helper for negating reusable, simple predicates used in preconditions, postconditions, and invariants"""
    @wraps(predicate)
    def negated_predicate(*args, **kwargs):
        return not predicate(*args, **kwargs)
    return negated_predicate

class argument_types:
    """DBC helper for reusable, simple predicates for argument-type tests used in preconditions"""
    def __init__(self, *typelist):
        self.typelist = typelist
        self.msg = "implementation error in argument_types"

    def __call__(self, s, *args, **kwargs):
        for typ, arg in zip(self.typelist, args):
            if not isinstance(arg, typ) and arg is not None:
                self.msg = "argument %s was not of type %s" % (arg, typ.__name__)
                return False
        return True

    def error(self):
        return self.msg 

def immutable(self, old, ret, *args, **kwargs):
    """Object immutability was violated by the method call (did you forget to override __eq__?)"""
    return old == self 
