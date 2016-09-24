### Parsing and pretty printing 

# Syntax:
# <expr> ::= <literal> | <function> {<expr>} | <expr> <operator> <expr>
# Operands are parenthesized when they are operator applications with precedence ≤ that of the operator of the expression,
#  or if the operator is associative, < that of the operator.

from utils import *
