## Measuring distance between expressions

The edit distance used in the heuristic search is an extension of the Levenshtein distance for strings, such that the elementary moves that define the edit distance extend the elementary moves of the Levenshtein distance from characters to atoms (literals and variables) in general.
It measures the minimum number of the following elementary edits on expressions:
- The application of an atom to an atom, e.g. f -> (f x) and (f x) -> (f x y) = ((f x) y) [applying y to (f x)] or (f (x y)) [applying y to x]
- The removal of the last atom from an application, e.g. (f x y) = ((f x) y) -> (f x) [removing y from (f x y)] or (f y) [removing x from (f x)]
- The substitution of one atom with another.

This metric allows for a number of possible choices of consistent heuristics, such as
- The deep length of an expression (minus one), i.e. the number of literals in the expression, which is consistent as at least n elementary edits, namely applications, are required to increase or decrease the deep length of an expression by n;
- The number of free variables in the expression, which is always less than or equal to the deep length;
- The maximum depth of the expression, which is consistent with the edit distance since each increment in depth requires at least one application, and each decrement at least one removal. Here we assume (f x y) = ((f x) y) has depth 1, whereas (f (x y)) has depth 2, as the former is still one function application but the latter requires 2.
The first choice, in fact, represents the distance of the expression to a literal, more specifically its topmost literal, and as such should be especially compatible with the distance metric.

### Modifying the distance and heuristic based on the content of expressions

If the edit distance and heuristic are supposed to measure the approximate cost of proving a given statement, it stands to reason that they might be dependent on the content of the statement. A few reasonable adjustments to the metric defined above can be made relating to logical operations such as conjunction, disjunction and implication. We might, for example, make the following assumptions about the cost of the application of such operations:
- The cost of a conjunction is the sum of the costs of its conjuncts, as in order to prove a conjunction, it is necessary to prove each conjunct separately.
- The cost of a disjunction is the minimum of the costs of its disjuncts, as it is only necessary to prove one disjunct to prove the entire disjunction.
- The cost of an implication is less than or equal to the cost of its consequent, as its proof requires the proof of its consequent assuming the truth of its antecedent.

We may generalize this notion by allowing the distance and heuristic to apply for the application of particular functions a particular associative binary operation on the distance/cost of each of their arguments. If the function f is associated with the operation o, we may extend the heuristic h and distance d into the heuristic h' and distance d' as in the following pseudocode (if h is defined as distance to a literal or to True, there is no need to redefine it separately):

```
h'(expr) = if expr = (f x y) then h'(x) o h'(y) else h(expr)
d'(expr1, expr2) =
  if expr1 = (f x1 y1) and expr2 = (f x2 y2) then
    d'(x1, x2) o d'(y1, y2) # or if f (and thus o) is commutative, min(d'(x1, x2) o d'(y1, y2), d'(x1, y2) o d'(x2, y1))
  else if expr1 = (f x1 y1) then
    d'(x, expr2) o d'(y, expr2)
  else if expr2 = (f x2 y2) then
    d'(expr1, x2) o d'(expr1, y2)
  else d(expr1, expr2) # If the definition of d is itself recursive, replace all recursive references to d with d' as well
```

Then, a natural question to ask is when this extension preserves the consistency of the heuristic with the distance metric. If we assume h is consistent with d, the demonstration that h' is consistent with d' follows via induction from the demonstration that for all expressions x and y, assuming that if h' is consistent for x and y, i.e. for all z `h'(x) ≤ d'(x, z) + h'(z)` and `h'(y) ≤ d'(y, z) + h'(z)`, h' is also consistent for (f x y).

This can be readily demonstrated for disjunction, for example, where o is the minimum operation. Given an arbitrary expression z, assuming `h'(x) ≤ d'(x, z) + h'(z)` and similarly for y, and assuming wlog that `h'(x) ≤ h'(y)`, `h'(x or y) = min(h'(x), h'(y)) = h'(x)`. If `d'(x, z) ≤ d'(y, z)`, then `d'(x or y, z) = d'(x, z)`, and since `h'(x) ≤ d'(x, z) + h'(z), h'(x or y) ≤ d'(x or y, z) + h'(z)`. And if `d'(y, z) ≤ d'(x, z)`, then `h'(x) ≤ h'(y) ≤ d'(y, z) + h'(z)`, so again `h'(x or y) ≤ d'(x or y, z) + h'(z)`. 
We need not check separately for the case of z itself being a disjunction, as it can be omitted from the definition of d' altogether. For this specific operation, we may derive the first clause of the definition of d' from the second and third clauses: `d'(x1 or y1, x2 or y2) = min(d'(x1, x2 or y2), d'(y1, x2 or y2)) = min(min(d'(x1, x2), d'(x1, y2)), min(d'(y1, x2), d'(y1, y2))) = min(min(d'(x1, x2), d'(y1, y2)), min(d'(x1, y2), d'(y1, x2)))`.

It is even simpler to demonstrate this for implication, where o is defined such that x o y = y. As `h'(x implies y) = h'(y)` and `d'(x implies y, z) = d'(y, z)`, the consistency of h' follows trivially from the assumption `h'(y) ≤ d'(y, z) + h'(z)` for all expressions z.

However, such a demonstration for conjunction, and its corresponding operation of addition, is more difficult, if at all possible. From the assumptions of consistency for x and y we have `h'(x and y, z) = h'(x, z) + h'(y, z) ≤ d'(x, z) + h'(z) + d'(y, z) + h'(z) = d'(x and y, z) + 2 h'(z) ≠ d'(x and y, z) + h'(z)`. 
For the special case of z itself being a conjunction we can still prove consistency: `|h'(x1 and y1) - h'(x2 and y2)| = |h'(x1) + h'(y1) - h'(x2) - h'(y2)| = |(h'(x1) - h'(x2)) + (h'(x2) - h'(y2))| = |(h'(x1) - h'(y2)) + (h'(y1) - h'(x2))|`. 
By assumption, for all z `|h'(x) - h'(z)| ≤ d'(x, z)`, and similarly for y. Then if `d'(x1, x2) + d'(y1, y2) ≤ d'(x1, y2) + d'(x2, y1)`, `|(h'(x1) - h'(x2)) + (h'(x2) - h'(y2))| ≤ |h'(x1) - h'(x2)| + |h'(x2) - h'(y2)| ≤ d'(x1, x2) + d'(y1, y2) = d'(x1 and y1, x2 and y2)`, and otherwise, `|(h'(x1) - h'(y2)) + (h'(y1) - h'(x2))| ≤ |h'(x1) - h'(y2)| + |h'(x2) - h'(y1)| ≤ d'(x1, x2) + d'(y1, y2) = d'(x1 and y1, x2 and y2)`, so in either case, h' is consistent.
For the general case, we can only show that h' is admissible, which follows from the aforementioned inequality `h'(x and y, z) ≤ d'(x and y, z) + 2 h'(z)` for all z satisfying h'(z) = 0. Then we may make the heuristic consistent by replacing the sum with an average, but that would contradict the associativity of and. We may use the pathmax equation to convert the heuristic into a consistent one, or we may restrict the domain of transformations on conjunctions to either literal Booleans or other conjunctions, in which case the heuristic will be consistent.

Or we may use another operation altogether to represent the cost of a conjunction, such as max, chosen so that it will complement min the same way conjunction complements disjunction in Boolean algebras. The heuristic and distance measure corresponding to such an operation, though difficult to make sense of from the perspective of measuring the cost of a proof, exhibit favorable properties in relation to consistency.
Given expressions x and y, assuming h' is consistent with d' for x and y and assuming wlog that `h'(x) ≥ h'(y)`, for all expressions z that are not conjunctions we have `h'(x and y) = max(h'(x), h'(y)) = h'(x) ≤ d'(x, z) + h'(z) ≤ max(d'(x, z), d'(y, z)) + h'(z) = d'(x and y, z) + h'(z)`. 
For the special case of z itself being a conjunction, say t and u, for `d'(x and y, t and u) + h'(t and u) = min(max(d'(x, t), d'(y, u)), max(d'(x, u), d'(y, t))) + max(h'(t), h'(u))`

## To do, notes

- Generalize the application semantics of each rule formed by a given predicate, from this ad hoc implementation that separates = and implies from other literals.
- Conjunctions and disjunctions also have nontrivial application semantics. If p and q transforms x into y and z respectively, (and p q) should transform x into either y or z, and (or p q) should transform it into (or y z) if y and z are predicates, and (or (= x y) (= x z)) otherwise.
- Verify the triangle inequality for extensions of the distance measure and define the heuristic as the distance to True, or to any literal.
- Establish recursive relations for the distance metric, based on the fact that the moves applicable to an expression either transform each argument or add or delete arguments. Work out exact expressions for the cost of replacing a function in an application with another, permuting arguments, etc.
- Try strategies out in batches, first trying one set of transformations for a statement and trying another set later. Such a method can perhaps be implemented within the A* search algorithm by pushing rules paired with strategies to the priority queue, or pushing statements and strategies in alternation.