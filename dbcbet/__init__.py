
"""
dbcbet Design-by-Contract with Bounded Exhaustive Testing

dbcbet is a Design-by-Contract library for python which uses predicates 
written in python as preconditions, postconditions, and invariants. We also
add a throws component to contracts.

Precondition - A precondition applies to a method and allows a predicate 
to test the state of self and the arguments before the method is invoked.
Returning False from a precondition predicate indicates that the contract
for calling the method was unsatisfied by the caller. 

Postcondition - A postcondition applies to a method and allows a predicate
to test the state of the preimage of self, the postimage of self, the return value,
and the arguments. The postcondition indicates the part of the contract which
must be fulfilled by the method implementation. A postcondition which returns
False indicates that there is a bug in the callee.

Invariant - An invariant applies to a class. The invariant for a class should
not be violated as viewed from the outside. For this reason, the invariant is
tested after every public method call (including methods like __str__ and __init__).

Throws - A guard on the allowable types of exceptions from a method. If the method
raises a different type of exception than in the allowed list, the exception is wrapped
in a ThrowsViolation.

If any of the contract components are violated, an exception is thrown. These are
PreconditionViolation, PostconditionViolation, InvariantViolation, and ThrowsViolation.
All derive from ContractViolation.

dbcbet is also a Bounded Exhaustive Testing tool. When a contract is in place on a
class, a few potential inputs for each method argument is sufficient to generate a 
great many tests using combinatorics. Combinations of arguments which violate 
preconditions are not bugs in the code (the method should not have been called 
with those arguments). Arguments which satisfy the precondition but result in a 
postcondition violation do, however, indicate bugs.
"""
