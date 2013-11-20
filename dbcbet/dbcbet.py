
"""
dbcbet: The library for design-by-contract

The public API is:
@inv(some_predicate) and @dbc applied to a class
@pre(some_predicate) and @post(some_predicate) applied to a method
@pre_final applied to a method
@throws(exception1, ...) applied to a method
The functions (predicates) used by the decorators have different 
signatures based on the type of contract component and on the 
signature of the method they apply to
"""

class inv(object):
    """A callable object (decorator) which attaches an invariant to a class"""
    def __get__(self, instance, owner):
        from types import MethodType
        return MethodType(self, instance, owner)

    def __init__(self, invariant, inherit=True):
        self.invariant = invariant
        self.inherit=inherit

    def __call__(self, clazz):
        self.clazz = clazz
        if hasattr(clazz, "_invariant_class") and clazz._invariant_class == clazz.__name__:            
            clazz._invariant.append(self.invariant)
        else:
            clazz._invariant = [self.invariant]
            clazz._invariant_class = clazz.__name__
        ensure_invoker(self.clazz)
        if self.inherit:
            inherit_contract(clazz)
        return clazz

def ensure_invoker(class_):
    import inspect
    mets = inspect.getmembers(class_, predicate=inspect.ismethod)
    for methodname, method in mets:
        if is_public(methodname):
            if not hasattr(method, "_invoker_exists"):
                setattr(class_, methodname, create_invoker(method))

def check_preconditions(wrapped_method, s, *args, **kwargs):
    violations = []
    if not hasattr(wrapped_method, "_precondition"):
        return
    for pred_list in wrapped_method._precondition:
        for pred in pred_list:
            if not pred(s, *args, **kwargs):
                violations.append(pred)
                break
        else:
            # pred_list was exhausted with no break
            return
    raise PreconditionViolation(violations, s, wrapped_method.__wrapped__, args, kwargs)                    

def check_postconditions(wrapped_method, s, old, ret, *args, **kwargs):
    if not hasattr(wrapped_method, "_postcondition"):
        return
    for pred in wrapped_method._postcondition:
        if not pred(s, old, ret, *args, **kwargs):
            raise PostconditionViolation(pred, s, old, ret, wrapped_method.__wrapped__, args, kwargs)

def check_invariants(wrapped_method, s, *args, **kwargs):
    if not hasattr(s.__class__, "_invariant"):
        return
    for pred in s.__class__._invariant:
        if not pred(s):
            raise InvariantViolation(pred, s, wrapped_method.__wrapped__, args, kwargs)

def check_throws(wrapped_method, ex, s, *args, **kwargs):
    """Exceptions are checked against the contractually allowed types."""
    # suppport underspecification, no @throws means all exceptions allowed
    if not hasattr(wrapped_method, "_throws"):
        return True
    
    # ContractViolations are treated differently from other ThrowsViolations
    check = wrapped_method._throws + [ContractViolation]

    # See if the exception was in the permitted list
    for exception_type in check:
        if isinstance(ex, exception_type):
            return True

    # Exception was not allowed
    raise ThrowsViolation(ex, s, wrapped_method.__wrapped__, args, kwargs)

def create_invoker(method):
    """One wrapper checks all contract components and invokes the method."""
    from functools import wraps
    @wraps(method)
    def wrapped_method(s, *args, **kwargs):
        check_preconditions(wrapped_method, s, *args, **kwargs)

        # A deep copy of the object and arguments are created for the postcondition
        o = old(method, s, args, kwargs)

        try:
            ret = method(s, *args, **kwargs)
            
            check_postconditions(wrapped_method, s, o, ret, *args, **kwargs)
            check_invariants(wrapped_method, s, *args, **kwargs)
        except Exception as ex:
            if check_throws(wrapped_method, ex, s, *args, **kwargs):
                raise
        return ret

    wrapped_method.__wrapped__ = method
    wrapped_method._invoker_exists = True
    return wrapped_method

def dbc(clazz):
    """A callable object (decorator) which applies the inheritance of a contract without applying an invariant"""
    ensure_invoker(clazz)
    inherit_contract(clazz)
    return clazz

def propogate_unwrapped(method):
    while True:
        try:
            if hasattr(method, "__wrapped__"):
                unwrapped = method.__wrapped__
                preserve_contracts_instance(unwrapped, method)
                method = unwrapped
            else:
                break
        except AttributeError:
            break

# def preserve_contracts(wrapped_method, method):
#     if hasattr(method, "_postcondition"): wrapped_method._postcondition = method._postcondition
#     if hasattr(method, "_precondition"): wrapped_method._precondition = method._precondition
#     if hasattr(method, "_invariant"): wrapped_method._invariant = method._invariant
#     if hasattr(method, "_throws"): wrapped_method._throws = method._throws
 
def preserve_contracts_instance(wrapped_method, method):
    if hasattr(method.__func__, "_postcondition"):
        try:
            wrapped_method.__func__._postcondition = method.__func__._postcondition
        except AttributeError:
            wrapped_method._postcondition = method.__func__._postcondition
    if hasattr(method.__func__, "_precondition"):
        try:
            wrapped_method.__func__._precondition = method.__func__._precondition
        except AttributeError:
            wrapped_method._precondition = method.__func__._precondition
    if hasattr(method.__func__, "_throws"):
        try:
            wrapped_method.__func__._throws = method.__func__._throws
        except AttributeError:
            wrapped_method._throws = method.__func__._throws
 
#
# This is how we handle inheritance
#
def inherit_contract(clazz):
    for baseclass in clazz.__bases__:
        if check_contract_inherited(clazz, baseclass):
            inherit_invariant_from(clazz, baseclass)
            inherit_method_contract_components_from(clazz, baseclass)
            declare_contract_inherited(clazz, baseclass)

def check_contract_inherited(clazz, baseclass):
    return not hasattr(clazz, "_inherited_contract_from") or baseclass.__name__ not in clazz._inherited_contract_from

def declare_contract_inherited(clazz, baseclass):
    if hasattr(clazz, "_inherited_contract_from"):
        clazz._inherited_contract_from.append(baseclass.__name__)
    else:
        clazz._inherited_contract_from = [baseclass.__name__]

def inherit_invariant_from(clazz, baseclass):
    if hasattr(baseclass, "_invariant"):
        for pred in baseclass._invariant:
            inv(pred, inherit=False)(clazz)

def inherit_method_contract_components_from(clazz, baseclass):
    import inspect
    mets = inspect.getmembers(clazz, predicate=inspect.ismethod)
    for methodname, method in mets:
        if is_public(methodname):
            # is there anything to inherit from?
            if hasattr(baseclass, methodname):
                baseclass_version = getattr(baseclass, methodname)
                # is there anything to inherit?
                if hasattr(baseclass_version, "_precondition"):
                    pre(baseclass_version._precondition)._compose_baseclass_precondition(method.__func__, baseclass_version)
                if hasattr(baseclass_version, "_postcondition"):
                    setattr(method.__func__, "_postcondition", post(baseclass_version._postcondition).compose_list(method.__func__))
                if hasattr(baseclass_version, "_throws"):
                    setattr(method.__func__, "_throws", throws(*tuple(baseclass_version._throws)).compose_list(method.__func__))
                propogate_unwrapped(method)

#
# Some helper functions used by the invariant class
#

def is_public(methodname):
    """Determines if a method is public by looking for leading underscore.
    
    pseudo-public methods are skipped"""
    return methodname[0] != "_" or methodname == "__str__" or methodname == "__init__" or methodname == "__eq__" or methodname == "__hash__"

#
# reduce(lambda x, y: x and y, map(has_property, list), 1)
# reduce(lambda x, y: x or y, map(has_property, list), 0)
#

class ContractViolation(Exception):
    """Base class for all contract violation classes"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
        
    def predicate_string(self, predicate):
        outstring = str(predicate.__name__)
        if hasattr(predicate, "error"):
            outstring = predicate.error()
        elif hasattr(predicate, "__doc__") and predicate.__doc__ is not None:
            outstring = predicate.__doc__
        return outstring

class PreconditionViolation(ContractViolation):
    def __init__(self, predicate_list, instance, method, *args, **kwargs):
        self.predicate_list = predicate_list
        self.instance = instance
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        outstring = "Precondition Violation: Instance of %s failed when calling %s with arguments (%s), keywords %s. Contract: %s" % (self.instance.__class__.__name__, self.method.__name__, ', '.join(map(str,self.args)), self.kwargs, ', '.join(map(self.predicate_string, self.predicate_list)))
        return outstring

class PostconditionViolation(ContractViolation):
    def __init__(self, predicate, instance, old, ret, method, args, kwargs):
        self.predicate = predicate
        self.instance = instance
        self.old = old
        self.ret = ret
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        outstring = "Postcondition Violation: Instance of %s with initialization failed when calling %s with arguments (%s), keywords %s, old values: %s, return: %s. Contract: %s" % (self.instance.__class__.__name__, self.method.__name__, ', '.join(map(str,self.args)), self.kwargs, self.old, self.ret, self.predicate_string(self.predicate))
        return outstring

class InvariantViolation(ContractViolation):
    def __init__(self, predicate, instance, method, args, kwargs):
        self.predicate = predicate
        self.instance = instance
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        outstring = "Invariant Violation: Instance of %s failed when calling %s with arguments (%s), keywords %s. Contract: %s" % (self.instance.__class__.__name__, self.method.__name__, ', '.join(map(str,self.args)), self.kwargs, self.predicate_string(self.predicate))
        return outstring

class ThrowsViolation(ContractViolation):
    def __init__(self, exception, instance, method, args, kwargs):
        self.exception = exception
        self.instance = instance
        self.method = method
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        outstring = "Throws Violation: Instance of %s failed when calling %s with arguments (%s), keywords %s. Threw %s" % (self.instance.__class__.__name__, self.method.__name__, ', '.join(map(str, self.args)), self.kwargs, str(type(self.exception)))
        return outstring

class throws(object):
    """A callable object (decorator) which attaches an allowable exception type to a method"""
    def __get__(self, instance, owner):
        from types import MethodType
        return MethodType(self, instance, owner)

    def __init__(self, *exceptions):
        self.exceptions = list(exceptions)

    def __call__(self, method):
        if hasattr(method, "_invoker_exists"):
            wrapped_method = method
        else:
            wrapped_method = create_invoker(method)
        # this allows additional exceptions
        self.compose(method, wrapped_method)
        return wrapped_method

    def compose(self, method, wrapped_method):
        # append acceptable throws
        if hasattr(method, "_throws"):
            method._throws.extend(self.exceptions)
            wrapped_method._throws = method._throws
        else:
            wrapped_method._throws = self.exceptions

    def compose_list(self,method):
        # each element of the throws list should either be 
        # 1. in the superclass list or 
        # 2. have a superclass in the superclass list
        if hasattr(method, "_throws"):
            for ex in method._throws:
                if not (ex in self.exceptions or issubclass(ex, tuple(self.exceptions))):
                    raise ContractViolation("throws has an implicit precondition: the exception or a supertype of the exception must be in the supertype throws list")
            return method._throws
        return self.exceptions
        
        if hasattr(method, "_throws"):
            method._throws.extend(self.exceptions)
            return method._throws
        return self.exceptions

class pre(object):
    """A callable object (decorator) which attaches a precondition to a method"""
    def __get__(self, instance, owner):
        from types import MethodType
        return MethodType(self, instance, owner)

    def __init__(self, precondition):
        self.precondition = precondition

    def __call__(self, method):
        if hasattr(method, "_invoker_exists"):
            wrapped_method = method
        else:
            wrapped_method = create_invoker(method)
        # this conjuncts existing preconditions (chained preconditions)
        self.compose(method, wrapped_method)
        return wrapped_method

    def compose(self, method, wrapped_method):
        # possibly replace the precondition with the conjunct of previous preconditions
        if hasattr(method, "_precondition"):
            method._uninherited_precondition.append(self.precondition)
            wrapped_method._uninherited_precondition = method._uninherited_precondition
            wrapped_method._precondition = method._precondition
        else:
            wrapped_method._uninherited_precondition = [self.precondition]
            wrapped_method._precondition = [wrapped_method._uninherited_precondition]
    
    def _compose_baseclass_precondition(self,method,baseclass_method):
        if hasattr(method, "_precondition"):
            if not hasattr(baseclass_method, "_final_pre"):
                method._precondition.extend(self.precondition)
            else:
                method._precondition[0:len(method._precondition)] = []
                method._precondtion.extend(self.precondition)
        else:
            method._uninherited_precondition = []
            method._precondition = [method._uninherited_precondition, self.precondition]
        if hasattr(baseclass_method, "_final_pre"):
            method._final_pre = True

class post(object):
    """A callable object (decorator) which attaches a postcondition to a method"""
    def __get__(self, instance, owner):
        from types import MethodType
        return MethodType(self, instance, owner)
    
    def __init__(self, postcondition):
        self.postcondition = postcondition

    def __call__(self, method):
        if hasattr(method, "_invoker_exists"):
            wrapped_method = method
        else:
            wrapped_method = create_invoker(method)
        # this conjuncts existing postconditions
        self.compose(method, wrapped_method)
        return wrapped_method

    def compose(self, method, wrapped_method):
        # possibly replace the postcondition with the conjunct of previous postcondition
        if hasattr(method, "_postcondition"):
            method._postcondition.append(self.postcondition)
            wrapped_method._postcondition = method._postcondition
        else:
            wrapped_method._postcondition = [self.postcondition]

    def compose_list(self,method):
        # possibly replace the postcondition with the conjunct of previous postcondition
        if hasattr(method, "_postcondition"):
            method._postcondition.extend(self.postcondition)
            return method._postcondition
        return self.postcondition

class old(object):
    """A nicer interface for old in postconditions"""
    def __init__(self, method, s, args, kwargs):
        """Performs a deep copy of self (s, not the current old-self), args, and kwargs"""
        import copy
        self.self = copy.deepcopy(s)
        self.args = copy.deepcopy(args)
        self.kwargs = copy.deepcopy(kwargs)

    def __repr__(self):
        return "old(self=%s,args=%s,kwargs=%s)" % (self.self, self.args, self.kwargs)
    
#
# Bounded exhaustive testing support
#
class bet(object):
    """The Bounded Exhaustive Testing class"""
    def __init__(self, clazz):
        """Binds us to the class"""
        self.clazz = clazz
        self.invariant_violations = 0
        self.precondition_violations = 0
        self.failures = 0
        self.successes = 0
        self.candidates = 0
        self.method_call_candidates = 0
        self.running_log = []
        self.arg_scope = -1

    def with_arg_scope(self, scope):
        self.arg_scope = scope

    def run(self):
        """Intantiates all objects satisfying the invariant.
        Then, for each instance, calls each method with the finitization arguments satisfying the precondition.
        Deep copying is used."""
        for fs in enumerate(self.clazz):
            candidate = self.instantiate_with(self.clazz, fs)
            self.process_candidate(candidate, fs)
        if self.candidates == 0:
            candidate = self.instantiate_with(self.clazz, {})
            self.process_candidate(candidate, {})
        self.print_invoice()

    def process_candidate(self, candidate, fs):
        for pred in candidate._invariant:
            if not pred(candidate):
                self.invariant_violations += 1
                return
        self.process_methods(candidate, fs)
        self.candidates += 1

    def print_invoice(self):
        print "\n".join(self.running_log)
        print "Summary: "
        print " Instance Candidates: " + str(self.candidates)
        print " Invariant Violations: " + str(self.invariant_violations)
        print " Method Call Candidates: " + str(self.method_call_candidates)
        print " Precondition Violations: " + str(self.precondition_violations)
        print " Failures: " + str(self.failures)
        print " Successes: " + str(self.successes)

    def process_methods(self, candidate, fs):
        import inspect
        mets = inspect.getmembers(candidate, predicate=inspect.ismethod)
        for key, val in mets:
            if hasattr(val, "_bet_arguments"):
                self.call_method(candidate, fs, val)

    def call_with_args_and_precondition(self, candidate, fs, val, args):
        import copy
        candidate_copy = copy.deepcopy(candidate)
        if self.process_precondition(val, candidate_copy, args):
            self.call_with_args(candidate, fs, val, args)
        else:
            self.precondition_violations += 1

    def process_precondition(self, val, candidate, args):
        for predlist in getattr(val, "_precondition"):
            success = True
            for pred in predlist:
                if not pred(candidate, *args):
                    success = False
            if success:
                return True
        return False

    def call_with_args(self, candidate, fs, val, args):
        try:
            val(*args)
            self.successes += 1
        except ContractViolation as cv:
            self.log_call_failure(candidate, fs, val, args, cv)
            self.failures += 1

    def log_call_failure(self, candidate, fs, val, args, cv):
        self.running_log.append("instance of %s with initialization %s failed when calling %s with arguments %s. Reason: %s" % (candidate.__class__.__name__, fs, val.__name__, ', '.join(map(str,args)), cv))

    def log_precondition_not_found(self, val):
        self.running_log.append("No precondition found when attempting to call %s" % (val.__name__))

    def call_method(self, candidate, fs, val):
        for args in enumerate_args(val._bet_arguments, self.arg_scope):
            self.method_call_candidates += 1
            if hasattr(val, "_precondition"):
                self.call_with_args_and_precondition(candidate, fs, val, args)
            else:
                self.log_precondition_not_found(val)
                self.call_with_args(candidate, fs, val, args)

    def instantiate_with(self, clazz, fieldset):
        """Instantiates an object and sets its fields to the values in the dictionary"""
        instance = self.find_acceptable_instance(clazz)
        for k, v in fieldset.items():
            setattr(instance, k, v)
        return instance

    def find_acceptable_instance(self, clazz):
        import inspect
        mets = inspect.getmembers(clazz, predicate=inspect.ismethod)
        found = False
        for key, val in mets:
            if key == "__init__":
                found = True
                if hasattr(val, "_bet_arguments"):
                    return self.call_init(clazz, val)
                else:
                    return clazz()
        if not found:
            return clazz()

    def call_init(self, candidate, val):
        for args in enumerate_args(val._bet_arguments, self.arg_scope):
            try:
                return candidate(*args)
            except ContractViolation:
                pass

# I used to check the precondition separately, but it's more compact without it
# def call_init(candidate, val):
#     for args in enumerate_args(val._bet_arguments):
#         if hasattr(val, "_precondition"):
#             for pred in getattr(val, "_precondition"):
#                 if not pred(candidate, *args):
#                     break
#             try:
#                 return candidate(*args)
#             except ContractViolation:
#                 pass
#         else:
#             return candidate(*args)

class finitize(object):
    def __init__(self, finitization):
        self. finitization = finitization
        self.fieldset = finitization()

    def __call__(self, clazz):
        clazz._finitization_field_set = self.fieldset
        return clazz

class finitize_method(object):
    def __init__(self, *bet_arguments):
        self.bet_arguments = bet_arguments

    def __call__(self, method):
        method._bet_arguments = self.bet_arguments
        return method

# def enumerate_gen(ob):
#     """The generator version of instance enumeration."""
#     fieldvector = ob._finitization_field_set.keys()
#     indexvector = [0 for f in fieldvector]
#     maxindexvector = [len(ob._finitization_field_set[fi]) for fi in fieldvector]
#     while(indexvector):
#         yield dict( (key, ob._finitization_field_set[key][indexvector[fieldvector.index(key)]]) for key in fieldvector)
#         indexvector = increment_vec(indexvector, maxindexvector)

class enumerate_args(object):
    def __init__(self, arg, arg_scope):
        self.fieldvector = arg
        self.arg_scope = arg_scope
        self.indexvector = [0 for f in self.fieldvector]
        self.maxindexvector = [len(a) for a in arg]

    def __iter__(self):
        return self

    def next(self):
        self.arg_scope -= 1
        if self.arg_scope == -1:
            raise StopIteration
        if self.indexvector:
            ret = [self.fieldvector[pos][self.indexvector[pos]] for pos in xrange(len(self.indexvector))]
            self.indexvector = increment_vec(self.indexvector, self.maxindexvector)
            return ret
        else:
            raise StopIteration
        
    def __len__(self):
        return reduce(lambda x, y: x*len(y), self.ob._finitization_field_set.values(), 1)

class enumerate(object):
    """The iterator version of instance enumeration.
    This version supports len(), so BET can recurse on instances."""
    def __init__(self, ob):
        self.ob = ob
        if not hasattr(ob, "_finitization_field_set"):
            ob._finitization_field_set = {}
        self.fieldvector = ob._finitization_field_set.keys()
        self.indexvector = [0 for f in self.fieldvector]
        self.maxindexvector = [len(ob._finitization_field_set[fi]) for fi in self.fieldvector]

    def __iter__(self):
        return self

    def next(self):
        if self.indexvector:
            ret = dict( (key,self.ob._finitization_field_set[key][self.indexvector[self.fieldvector.index(key)]]) for key in self.fieldvector)
            self.indexvector = increment_vec(self.indexvector, self.maxindexvector)
            return ret
        else:
            raise StopIteration

    def __len__(self):
        return reduce(lambda x, y: x*len(y), self.ob._finitization_field_set.values(), 1)

def increment_vec(vec, max_vec):
    def hidden_increment(vec, max_vec, pos):
        if pos >= len(vec):
            return False
        if vec[pos] == max_vec[pos] - 1:
            vec[pos] = 0
            return hidden_increment(vec, max_vec, pos+1)
        vec[pos] = vec[pos]+1
        return vec
    return hidden_increment(vec, max_vec, 0)

