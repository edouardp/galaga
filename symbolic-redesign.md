# **Spec: Naming and Evaluation Semantics for Multivectors and Blades**







## **Goal**





Make symbolic use feel natural and reversible, without forcing the library to maintain two visibly separate worlds of “symbol” versus “multivector”.



The API should let a developer independently control:



1. **Identity / display**

   

   - named
   - anonymous

   

2. **Evaluation / representation**

   

   - lazy
   - eager

   





These are separate axes.



A value may be:



- named + eager
- named + lazy
- anonymous + eager
- anonymous + lazy





Basis blades returned from an algebra should be **named + eager by default**.



------





# **Core concepts**







## **1. Naming is metadata plus display behavior**





A multivector may optionally have a name.



Examples:



- e1
- B
- R
- psi





A name affects:



- how the object prints
- how the object may appear in symbolic expressions





A name does **not** change the mathematical value.





## **2. Lazy vs eager is about representation strategy**





A multivector may either:



- hold or prefer an unevaluated symbolic expression tree (**lazy**), or
- hold or prefer a concrete expanded multivector value (**eager**)





This is about how results are represented and printed, not about changing the mathematics.





## **3. Naming and laziness are orthogonal**





A thing can be:



- named but eager: basis blades should work like this
- named and lazy: useful for symbolic shorthand like B, R, psi
- anonymous and lazy: useful when preserving expression structure but not hiding it behind a label
- anonymous and eager: ordinary plain multivector behavior





------





# **Proposed API**







## **.name(label: str) -> Self**





Assign a name to the object.





### **Semantics**





- sets the display name to label
- does **not by itself require** changing the mathematical value
- if called on an anonymous object, it becomes named
- if called on an already named object, it replaces the previous name







### **Default behavior choice**





For ergonomics, calling .name(...) should also make the object **lazy by default** unless explicitly overridden elsewhere.



Reason:



- most of the time, when a developer names an expression, they want the name to stand in for the expression





Example:

```
B = (e1 ^ e2).name("B")
print(B)   # B
```

## **.anon() -> Self**





Remove the display name, but preserve the underlying value/expression.





### **Semantics**





- removes the object’s explicit name
- does not force eager evaluation
- if the object is lazy, it remains lazy, but now prints using its underlying expression
- if the object is eager, it remains eager





Example:

```
B = (e1 ^ e2).name("B")
print(B)        # B

B2 = B.anon()
print(B2)       # e1 ^ e2   (or expanded symbolic equivalent)
```



## **.lazy() -> Self**





Prefer lazy symbolic representation.





### **Semantics**





- preserves or creates an unevaluated symbolic form where possible
- if the object already has a symbolic expression tree, keep it
- if the object is currently eager and no expression history exists, lazy mode may simply wrap the current concrete value symbolically, or may remain effectively eager internally but behave as lazy for future operations. The spec does not require a particular implementation.







### **Important**





.lazy() does not assign a name.



Example:

```
x = (e1 + e2).lazy()
print(x)   # e1 + e2
```



## **.eager() -> Self**





Force eager evaluation.





### **Semantics**





- computes the concrete multivector value
- future printing should show the expanded/concrete form unless the object is still named and the printing rules choose otherwise
- eager evaluation does **not automatically remove the name**





This is important.



A named eager object is valid and useful.



Example:

```
B = (e1 ^ e2).name("B")
C = B.eager()
```



C should be:



- mathematically concrete
- still named B, unless explicitly anonymized





This allows named basis blades and named constants to remain pleasant to work with.



------





# **Printing rules**





Printing behavior should be predictable.





## **Rule 1: named objects print by name**





If an object has a name, printing it normally should print its name.



Example:

```
print(B)   # B
```

## **Rule 2: anonymous objects print by representation**





If unnamed:



- lazy objects print their symbolic structure
- eager objects print expanded multivector components





Example:

```
print((e1 ^ e2).lazy())    # e1 ^ e2
print((e1 ^ e2).eager())   # 1e12   or equivalent basis form
```

## **Rule 3: anonymizing reveals underlying structure**





Calling .anon() should expose the underlying representation.



Example:

```
B = (e1 ^ e2).name("B")
print(B)          # B
print(B.anon())   # e1 ^ e2   or expanded form depending on lazy/eager state
```

------





# **Basis blade behavior**







## **Requirement**





algebra.blades should return basis blades that are:



- **named**
- **eager**





by default.





### **Why**





Basis blades like e1, e2, e12 are fundamental values, not user-defined symbolic aliases. Developers expect them to:



- have stable names
- behave like real concrete blades immediately
- not carry avoidable symbolic laziness







### **Expected behavior**

```
alg = Algebra([1, 1, 1])
e1, e2, e3 = alg.blades

print(e1)         # e1
print(e1.eager()) # e1
print(e1.anon())  # [concrete blade representation]
```

Whether anon() on a basis blade prints e1 as a basis label or a lower-level component form is implementation-defined, but the API should treat the blade as an eager concrete object with a default name.





### **Spec note**





The spec does **not** require basis blades to be implemented as ordinary multivectors internally. It only requires that they present this interface and these semantics.



------





# **Evaluation rules**







## **.eval()**

##  **remains valid**





If the library already has .eval(), it should continue to exist.





## **Recommended semantic alignment**





Make .eval() equivalent to .eager() in value semantics.



That is:



```
x.eval()
```



should return the eager/concrete value.





## **Name propagation through** 

## **.eval()**





Recommended behavior:



- .eval() / .eager() **preserve the name**
- removing the name is the responsibility of .anon()





This cleanly separates the two axes:



- evaluation: .eager()
- naming: .anon()





Example:



```
R = ((e1 ^ e2) * 0.5).name("R")
print(R)           # R

Re = R.eager()
print(Re)          # R

print(Re.anon())   # expanded concrete form
```

This is cleaner than having .eval() silently destroy names.



------





# **Operation propagation rules**





Operations should propagate name and laziness in a principled way.





## **1. Names do not automatically propagate**





If you combine named things, the result should usually be anonymous unless explicitly named.



Example:

```
B = (e1 ^ e2).name("B")
x = (B + e3)
print(x)   # should print expression, not invent a new name
```

Reason:

automatic name propagation quickly becomes confusing.





## **2. Laziness propagates from operands**





If any operand is lazy, the result should generally be lazy.



Example:

```
B = (e1 ^ e2).name("B")    # named + lazy by default
x = B + e3
print(x)                   # symbolic expression
```

## **3. Eager with eager yields eager**





If all operands are eager, result should default to eager.



Example:

```
x = e1 + e2
print(x)   # concrete/expanded multivector form
```

## **4. Explicit mode-changing methods override defaults**

```
x = (B + e3).eager()
y = x.lazy()
```

------





# **Recommended state model**





Conceptually, each object should expose or behave as if it has:



- name: str | None
- is_lazy: bool
- value: concrete multivector value
- expr: optional symbolic expression tree





This is conceptual only. The implementation may differ.



------





# **Use cases**







## **Use case 1: plain numeric / algebraic use**

```
alg = Algebra([1, 1, 1])
e1, e2, e3 = alg.blades

x = 2*e1 + 3*e2
```

Expect:



- basis blades are named + eager
- result is eager if all inputs are eager







## **Use case 2: define a named symbolic bivector**

```
B = (e1 ^ e2).name("B")
print(B)   # B
```

Expect:



- object is named
- object is lazy by default after naming
- underlying value remains recoverable







## **Use case 3: reveal the symbolic structure again**

```
print(B.anon())   # e1 ^ e2
```

Expect:



- name removed
- lazy structure preserved







## **Use case 4: evaluate but keep the name**

```
Be = B.eager()
print(Be)         # B
print(Be.anon())  # concrete expanded form
```

## **Use case 5: rename an existing named object**

```
B2 = B.name("plane")
print(B2)   # plane
```

## **Use case 6: lazy unnamed expressions**

```
expr = ((e1 + e2) ^ e3).lazy()
print(expr)   # symbolic structure
```



## **Use case 7: rotor workflow**

```
B = (e1 ^ e2).name("B")
R = (-B * theta/2).exp().name("R")
v = e1
v_rot = R * v * ~R
```

Expected:



- B and R print as names
- v_rot is lazy if R is lazy
- v_rot.anon() reveals expression
- v_rot.eager().anon() reveals concrete rotated multivector







## **Use case 8: basis blades stay eager but can become lazy/named differently**

```
E = e1.name("E")
print(E)          # E
print(E.anon())   # e1 or concrete basis representation
```

## **Use case 9: symbolic shorthand over symbolic structure**

```
B = (e1 ^ e2).lazy()
print(B)          # e1 ^ e2

B = B.name("B")
print(B)          # B

print(B.anon())   # e1 ^ e2
```



## **Use case 10: evaluate without losing developer labels**

```
psi = complicated_expr.name("psi")
psi_eval = psi.eager()

print(psi_eval)        # psi
print(psi_eval.anon()) # expanded result
```

------





# **Non-goals**





The spec does not require:



- a particular internal class hierarchy
- separate Symbol and Multivector public classes
- preserving full symbolic history in every case
- a specific AST representation
- basis blades to literally be multivectors internally





The spec only defines observable API behavior.



------





# **Suggested method summary**







## **Required**

- .name(label: str) -> Self
- .anon() -> Self
- .lazy() -> Self
- .eager() -> Self

## **Existing compatibility**

* .eval() -> Self

- Recommended to behave like .eager()





------





# **Recommended defaults**







## **Default object construction**





- ordinary concrete algebraic operations on eager inputs produce eager unnamed results
- basis blades are named eager results







## **Default naming behavior**





- .name(label) should produce a named lazy object by default





This gives the developer the most useful shorthand behavior.



------





# **Edge-case decisions**







## **Calling** 

## **.name()**

##  **on eager object**





Allowed.



Result:



- named
- lazy by default





Example:

```
x = (e1 + e2)        # eager unnamed
y = x.name("y")      # named lazy
```

## **Calling** 

## **.name()**

##  **on already lazy named object**





Allowed.



Result:



- replace name only







## **Calling** 

## **.anon()**

##  **on anonymous object**





No-op.





## **Calling** 

## **.eager()**

##  **on already eager object**





No-op in semantics.





## **Calling** 

## **.lazy()**

##  **on already lazy object**





No-op in semantics.



------





# **Short examples block for the coding assistant**

```
alg = Algebra([1, 1, 1])
e1, e2, e3 = alg.blades   # named + eager

B = (e1 ^ e2).name("B")   # named + lazy
print(B)                  # B

print(B.anon())           # e1 ^ e2

Be = B.eager()            # named + eager
print(Be)                 # B
print(Be.anon())          # concrete expanded bivector

expr = (B + e3)           # lazy result
print(expr)               # symbolic expression involving B and e3

expr2 = expr.anon()       # anonymous but still lazy
print(expr2)              # expanded symbolic structure

expr3 = expr2.eager()     # anonymous eager
print(expr3)              # concrete multivector
```

------





# **Design rationale**





This split is nice because it avoids overloading one operation with too many responsibilities:



- .name() controls identity/display
- .anon() removes identity/display
- .lazy() controls symbolic representation
- .eager() controls concrete evaluation





And the important special case is covered cleanly:



- basis blades are **named + eager**
- user-defined shorthand objects are often **named + lazy**\



