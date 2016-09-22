# theorem-prover
Proof of concept for theorem proving using heuristic search

## Description

The theorem proving algorithm operates on expressions comprised of literals and universally quantified variables.
A statement is proven by a series of transformations that ends in the literal `True`. Such transformations can be separated into two rough categories: a rule being applied to an expression to yield another expression, and a rule matching a statement and yielding `True`. The program applies A* search on the resulting graph of expressions connected by such transformations to find the shortest path starting from an inputted statement and concluding in `True`. 

For example, the proof that addition, defined as in the Peano axioms, is associative, is represented by these transformations:
- `M + (N + K) = (M + N) + K`
- Induction on M => `0 + (N + K) = (0 + N) + K and M + (N + K) = (M + N) + K implies s M + (N + K) = (s M + N) + K`
- Application of rule `0 + N = N` => `N + K = N + K and M + (N + K) = (M + N) + K implies s M + (N + K) = (s M + N) + K`
- Application of rule `s M + N = s (M + N)` => `N + K = N + K and M + (N + K) = (M + N) + K implies s (M + (N + K)) = s ((M + N) + K)`
- Left conjunct matches rule `X = X` => `True and M + (N + K) = (M + N) + K implies s (M + (N + K)) = s ((M + N) + K)`
- Right conjunct matches rule `X = Y implies s X = s Y` => `True and True`
- Statement matches rule `True and True` => `True`
