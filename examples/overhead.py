"""Demonstrates the function call overhead of an empty contract.

Using contracts compared to using nothing has an unbound
overhead. Checks before and after a method can be arbitrarily
complex. If we assume a developer uses defensive programming
practices, guards inside a method will perform the same checks that
the programmer would program into contracts. Even still, the overhead
is potentially unbound because of a deep copy on the old self and
argument values performed by dbc. A programmer using defensive
programming is very unlikely to use a deep copy, but rather navigate
structures and save only relevant values. Simply saying that the
penalty is unbound isn't terribly useful. This example looks at the
minimum overhead, in absolute (rather than relative) terms.

On my machine the overhead is 60 micro-seconds per method call.
"""

from dbcbet.dbcbet import pre
import timeit

class NoContracts(object):
    def does_nothing(self):
        pass
    
def empty_precondition(self):
    """Using this precondition wraps the method with the dbc infrastructure"""
    return True
    
class Contracted(object):
    @pre(empty_precondition)
    def does_nothing(self):
        pass

def main():
    nc=NoContracts()
    c=Contracted()
    number = 10000
    without_contracts = timeit.Timer(nc.does_nothing).timeit(number=number)
    with_contracts = timeit.Timer(c.does_nothing).timeit(number=number)
    print "call overhead (in seconds): " + str((with_contracts - without_contracts)/number)

if __name__ == "__main__":
    main()
