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
    def chartype(c):
        if c.isalpha():
            return 0
        if c.isdigit():
            return 1
        return 2
    tokens = []
    word = ''
    ct = None
    for c in s:
        if word and (word in functions() or c.isspace() or chartype(c) != ct):
            if word in ['True', 'False']:
                word = eval(word)
            tokens.append(word)
            word = ''
        else:
            word += c
        ct = chartype(c)
    tokens.append(word)
    return tokens

def parse(tokens):
    'Parse list of tokens into an expression, either an atom or a tuple of expressions.'
    pass

def output(expr):
    'Convert expression into a readable string representation.'
    pass
