"""Test dbcbet"""

from dbcbet.dbcbet import pre, post, inv, throws, dbc, bet, finitize, finitize_method, ContractViolation, ThrowsViolation
from dbcbet.helpers import state, argument_types

#
# These methods are the various preconditions, postconditions, and invariants used by tests
#

# a precondition
def both_numbers_positive(self, arg1, arg2):
    return arg1 > 0 and arg2 > 0

# a (necessary) precondition
def first_greater_than_second(self, arg1, arg2):
    return arg1 > arg2

# a postcondition
def returned_the_sum(self, old, ret, arg1, arg2):
    return ret == arg1+arg2

# another postcondition
def set_x(self, old, ret, arg1, arg2):
    return self.x == arg1-arg2

# an invariant
def x_non_negative(self):
    return self.x >= 0

# a finitization
def finitize_test_class():
    return {'x':[-1,0,1,2]}

# Pete: this seems like a typical case. Maybe the finitization should just be the returned hash, and not a function.

#
# showing off the syntax
#

# applying invariant to class, precondition and postconditions to the method
@inv(x_non_negative)
@finitize(finitize_test_class)
class TestClass:
    def __init__(self):
        self.x = 0
    
    @finitize_method([-1,0,1,2,3],range(-1,3))
    @pre(both_numbers_positive)
    @pre(first_greater_than_second)
    @post(set_x)
    @post(returned_the_sum)
    def do_something(self, a1, a2):
        self.x = a1-a2
        return a1+a2
    
# Tests

# def testEnumerate():
#     class Foo(object):
#         pass
#     ob = Foo()
#     ob._finitization_field_set={"a":[-1,0,1], "b":['aa','bb','cc','dd'], "c":[-5]}
#     for vals in enumerate(ob):
#         print vals
#         #    for vals in enumerate(ob):
#         #print vals

# def test1():
#     t = TestClass()
#     try:
#         t.do_something(1,2)
#     except ContractViolation as e:
#         print e.value
#     t.do_something(2,1)
#     print t.x
#     try:
#         t.do_something(-1,2)
#     except ContractViolation as e:
#         print e.value
#     print "done"

def test_bet():
    bet(TestClass).run()

#
# A more complicated test with inheritance
#

def base_class_inv(self):
    if hasattr(self, "x"):
        return self.x != 1
    else:
        return True

def sub_class_inv(self):
    if hasattr(self, "x"):
        return self.x != 2
    else:
        return True

def base_class_method_pre(self, a):
    return a != 3

def sub_class_method_pre(self, a):
    return a != 4

def base_class_method_post(self, old, ret, a):
    return a != 5

def sub_class_method_post(self, old, ret, a):
    return a != 6

def sub_class_method_pre2(self, a):
    return a != 7

def sub_class_method_post2(self, old, ret, a):
    return a != 8

@inv(base_class_inv)
class TestBaseClass(object):
    @pre(base_class_method_pre)
    @post(base_class_method_post)
    def test_method(self, a):
        self.x = a

@inv(sub_class_inv)
class TestSubClass(TestBaseClass):
    @pre(sub_class_method_pre)
    @pre(sub_class_method_pre2)
    @post(sub_class_method_post)
    @post(sub_class_method_post2)
    @finitize_method(range(-1,10))
    def test_method(self, a):
        self.x = a+1

def test_inheritance():
    bet(TestSubClass).run()
    print "Individual Tests"
    test_explicit_success(TestSubClass, -1)
    test_explicit_fail(TestSubClass, 0)
    test_explicit_fail(TestSubClass, 1)
    test_explicit_success(TestSubClass, 2)
    test_explicit_success(TestSubClass, 3)
    test_explicit_success(TestSubClass, 4)
    test_explicit_fail(TestSubClass, 5)
    test_explicit_fail(TestSubClass, 6)
    test_explicit_success(TestSubClass, 7)
    test_explicit_fail(TestSubClass, 8)
    test_explicit_success(TestSubClass, 9)

def test_solo_composition():
    test_only_pre()
    test_only_post()
    test_only_inv()
        
class TestOnlyPre(object):
    @pre(sub_class_method_pre)
    @pre(sub_class_method_pre2)
    def test_method(self, a):
        self.x = a+1

def test_only_pre():
    test_explicit_fail(TestOnlyPre, 4)
    test_explicit_success(TestOnlyPre, 5)
    test_explicit_fail(TestOnlyPre, 7)
        
class TestOnlyPost(object):
    @post(sub_class_method_post)
    @post(sub_class_method_post2)
    def test_method(self, a):
        self.x = a+1

def test_only_post():
    test_explicit_fail(TestOnlyPost, 6)
    test_explicit_success(TestOnlyPost, 7)
    test_explicit_fail(TestOnlyPost, 8)

@inv(base_class_inv)
@inv(sub_class_inv)
class TestOnlyInv(object):
    def test_method(self, a):
        self.x = a+1

def test_only_inv():
    test_explicit_success(TestOnlyInv, -1)
    test_explicit_fail(TestOnlyInv, 0)
    test_explicit_fail(TestOnlyInv, 1)
    test_explicit_success(TestOnlyInv, 2)

def test_explicit_fail(class_, val):
    t = class_()
    try:
        t.test_method(val)
        print str(val) + " worked, should have failed"
    except ContractViolation as cv:
        print str(val) + " failed, as expected"

def test_explicit_success(class_, val):
    t = class_()
    try:
        t.test_method(val)
        print str(val) + " worked, as expected"
    except ContractViolation as cv:
        print cv
        print str(val) + " failed, should have worked"

class GoodException(Exception):
    pass

class BadException(Exception):
    pass

class AnotherGoodException(GoodException):
    pass

class ADifferentGoodException(Exception):
    pass
        
class ThrowsTestClass(object):
    @throws(ADifferentGoodException)
    @throws(GoodException)
    def do_something(self, x):
        if x==1:
            # allowed
            raise GoodException()
        if x==2:
            # allowed
            raise AnotherGoodException()
        if x==3:
            # allowed
            raise ADifferentGoodException()
        # not allowed
        raise BadException()

@dbc
class ThrowsTestSubClass(ThrowsTestClass):
    @throws(AnotherGoodException)
    def do_something(self, x):
        if x==1:
            # not allowed
            raise GoodException()
        if x==2:
            # allowed
            raise AnotherGoodException()
        if x==3:
            # not allowed
            raise ADifferentGoodException()
        # not allowed
        raise BadException()

@dbc
class ThrowsTestSubSubClass(ThrowsTestSubClass):
    def do_something(self, x):
        if x==1:
            # not allowed
            raise GoodException()
        if x==2:
            # allowed
            raise AnotherGoodException()
        if x==3:
            # not allowed
            raise ADifferentGoodException()
        # not allowed
        raise BadException()

def test_throws():
    try:
        ThrowsTestClass().do_something(1)
    except GoodException:
        print "GoodException worked"
    try:
        ThrowsTestClass().do_something(2)
    except GoodException:
        print "GoodException worked"
    try:
        ThrowsTestClass().do_something(3)
    except ADifferentGoodException:
        print "ADifferentGoodException worked"
    try:
        ThrowsTestClass().do_something(4) 
    except ThrowsViolation:
        print "Translating BadException to ThrowsViolation worked"
    try:
        ThrowsTestSubClass().do_something(1)
    except ThrowsViolation:
        print "Translating GoodException to ThrowsViolation on subclass worked"
    try:
        ThrowsTestSubClass().do_something(2)
    except GoodException:
        print "GoodException worked"
    try:
        ThrowsTestSubClass().do_something(3)
    except ThrowsViolation:
        print "Translating ADifferentGoodException worked"
    try:
        ThrowsTestSubClass().do_something(4) 
    except ThrowsViolation:
        print "Translating BadException to ThrowsViolation worked"
    try:
        ThrowsTestSubSubClass().do_something(1)
    except ThrowsViolation:
        print "Translating GoodException to ThrowsViolation on subsubclass worked"
    try:
        ThrowsTestSubSubClass().do_something(2)
    except GoodException:
        print "GoodException worked"
    try:
        ThrowsTestSubSubClass().do_something(3)
    except ThrowsViolation:
        print "Translating ADifferentGoodException worked"
    try:
        ThrowsTestSubSubClass().do_something(4) 
    except ThrowsViolation:
        print "Translating BadException to ThrowsViolation worked"
    
#
# A structural recursion test
#

# def no_cycles(self):
#     def recurse(node, visited):
#         if node.left is None and node.right is None:
#             return True
#         if node.left in visited:
#             return False
#         elif node.left is not None:
#             visited.append(node.left)
#             if not recurse(node.left, visited):
#                 return False
#         if node.right in visited:
#             return False
#         elif node.right is not None:
#             visited.append(node.right)
#             if not recurse(node.right, visited):
#                 return False
#         return True
#     return recurse(self, [])

# def test_no_cycles():
#     a = TestBinaryNode()
#     b = TestBinaryNode()
#     a.left = b
#     b.right = a
#     print no_cycles(a)

# def binary_node_finitization():
#     return {'left':TestBinaryNode, 'right':TestBinaryNode}

# @inv(no_cycles)
# @finitize(binary_node_finitization)
# class TestBinaryNode(object):
#     def __init__(self):
#         self.left = None
#         self.right = None

# def test_structural_recursion():
#     bet(TestBinaryNode).run()


#     import inspect
#     import sys
#     classname = inspect.getouterframes(inspect.currentframe())[1][3]

# this is how python does main, just so you can see the stuff in action
if __name__ == "__main__":
    test_inheritance()
    test_throws()
    test_bet()
    test_solo_composition()
