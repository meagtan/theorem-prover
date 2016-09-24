### Parsing and pretty printing 

# Syntax:
# <expr> ::= <atom> | <function> <whitespace> <expr> {<whitespace> <expr>} | <expr> <whitespace> <operator> <whitespace> <expr>
# Operands are parenthesized when they are operator applications with precedence ≤ that of the operator of the expression,
#  or if the operator is associative, < that of the operator.
# Function arguments are parenthesized if they are not atomic values, i.e. literals and variables. 

from utils import *

operators = ['*', '+', '=', 'implies', 'and', 'or'] # sorted by precedence

def functions():
    return (f for f in literals if isinstance(literals[f], tuple))

def tokenize(s):
    'Split string representing an expression into tokens.'
    tokens = []
    word = None
    for c in s:
        pass

def parse(tokens):
    'Parse list of tokens into an expression, either an atom or a tuple of expressions.'
    pass

def output(expr):
    'Convert expression into a readable string representation.'
    pass
