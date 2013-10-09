#
# The bet for systems class
#

#
# Usage 1: bet(class, method).run()
# Usage 2: bet(classes, methods).run()
# if the first parameter has a fieldset, the system treats it as a class
# if the first parameter does not have a fieldset, the system treats it as a list
# an empty fieldset generates a single instance of the no-argument constructor
# if a fieldset has a type, the system recurses (finite depth) and attempts to create a finitization for that type
# a zero-argument constructor is not necessary if there is a finitization for the __init__ method that eventually produces a valid instance
class bet_invoice(object):
   def __init__(self):
        self.invariant_violations = 0
        self.precondition_violations = 0
        self.failures = 0
        self.successes = 0
        self.candidates = 0
        self.method_call_candidates = 0
        self.running_log = []

   def print_invoice(self):
      pass

#
# Problem - given some types A, B, C, ..., generate a set of instances for each type for use in tests.
# Assume None is a valid and important instance for testing.
# Note that references can be circular.
# We are interested in bounded exhaustive testing a system.
# Let us define construction-realizable configurations as those that can be realized by calling only constructors.
# Let us define assignment-realizable configurations as those that are construction-realizable or configurations that can be reached from construction-realizable configuraions via assignment (no method calls).
# Let us define realizable configurations as all configurations of a system that are reachable from construction-realizable configurations via assignment and method calls.
# For a language without private data, all realizable configurations are assignment-realizable
# We wish to explore all realizable configurations within a bound. From those configurations, we wish to call methods and observe the outcome, then revert the system so that the next method call might be attempted.
# Because a system might have external state (like a database), a hook should be provided to revert the external state, possibly iterating over multiple external states.
# What might this look like?
# for external_state in external_states:
#   for configuration in configurations:
# ...
#
# or
#
# for configuration in configurations:
#   for external_state in external_states:
# ...
#
# Let's make some assumption:
#  If fields aren't created and deleted at runtime, we can generate a configuration from the current fieldset for all objects in that configuration.
#  Global objects can be described and put into the system. If there is a global integer named foo, then __module__.foo probably could have a finitization.
#
# Do we have to be careful about object pool numbers?
# Suppose we have a system with 2 types: parents and children
# The system is constrained in such a way that each parent must have 2 distinct children not shared by any other parent
# This system obviously ony has a valid configuration if the number of children is twice the number of parents

   
class bet(object):
    """The Bounded Exhaustive Testing class"""
    def __init__(self, clazz, test=None):
        """Binds us to the class"""
        self.clazz = clazz
        self.test = test
        self.object_pool = {}
        self.invoice = bet_invoice()

    def run(self):
        """Intantiates all objects satisfying the invariant.
        Then, for each instance, calls each method with the finitization arguments satisfying the precondition.
        Deep copying is used."""
        for candidate in self.enumerate_candidates():
           #c andidate = instantiate_with(self.clazz, fs)
            self.process_candidate(candidate, fs)
        if self.candidates == 0:
            candidate = instantiate_with(self.clazz, {})
            self.process_candidate(candidate, {})
        self.invoice.print()

   def run2(self):
      for external_state in external_states:
         for configuration in configurations:
            for obj in configuration.objects:
               for method in obj:
                  call_method(method)
                  revert_to_previous_configuration_and_external_state() 

# should we make an object pool support lazy iniitalization?
# generating objects otherwise seems circular in the worst case.
class lazy_pool(object):
   pass

class Tester:
   """Bounded Exhaustive Testing for a class Using Design-by-Contract"""

   def __init__(clazz):
      pass

   def test():
      pass

class TestEnumerator:
   """Enumerates tests for bounded exhaustive testing"""

   def __init__(clazz):
      pass

   def __init__():
      pass

   def methods(self):
      """returns a list of public methods for the object"""
      pass

   def arity(self, method):
      """returns the number of formal parameters for a method"""
      pass

   def check_pre(self, method, params):
      """is the precondition satisfied?"""
      pass



if __name__ == "__main__":
   print "test"
