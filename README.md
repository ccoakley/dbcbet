dbcbet
======

Design by Contract with Declarative Bounded Exhaustive Testing

Design-by-Contract (DbC) is a language feature introduced in Eiffel. 
Though object-oriented, contracts are orthogonal to its type system: 
One cannot ask for a precondition's type, inspect a postcondition's fields, or reuse/extend a class invariant. 
DbC is implementable in languages such as Java and Python using features like reflection, bytecode manipulation, and 
annotations. 
As in Eiffel, extant DbC contract implementations are orthogonal to their type systems.

Our Python DbC implementation embraces the idea that in a "pure" object-oriented system, "everything is an object." 
We thus enable concise reuse of common constraints such as non-nullity of fields, integer bounds, and string size limits, 
with syntax that is similar to that used by Object-Relational Mapping libraries that allow field constraints. 
We explore and demonstrate contract components as objects.

In Bounded Exhaustive Testing (BET), the combinatoric explosiveness of exhaustive testing is bounded via Finitizations: 
methods that enumerate a subset of an object's set of field values. 
While extant research on BET notes that DbC facilitates automated testing, DbC and BET are distinct concepts. 
We extend DbC to optionally include finitization, synergistically integrating DbC and BET. 
Unit testing is transformed from four procedural tasks:

<ol>
<li>
1) initialize object states,</li>
</ol>
2) generate method inputs,
3) invoke an object's methods, and
4) compare returned values and resultant state with expected values and state

to two declarative tasks: define contracts and enumerate inputs of interest.

Performance experiments are presented. 
