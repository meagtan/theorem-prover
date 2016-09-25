### Parsing and pretty printing 

# Syntax:
# <expr> ::= <atom> | <function> <whitespace> <expr> {<whitespace> <expr>} | <expr> <whitespace> <operator> <whitespace> <expr>
# Operands are parenthesized when they are operator applications with precedence ≤ that of the operator of the expression,
#  or if the operator is associative, < that of the operator.
# Function arguments are parenthesized if they are not atomic values, i.e. literals and variables. 

from utils import *

operators = ['*', '+', '=', 'implies', 'and', 'or'] # sorted by precedence

# memoize this until literals is changed
def functions():
    return (f for f in literals if isinstance(literals[f], tuple) and f not in operators)
def atoms():
    return (v for v in literals if not isinstance(literals[v], tuple))

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
        if not c.isspace():
            word += c
        ct = chartype(c)
    tokens.append(word)
    return tokens

def parse(tokens):
    'Parse list of tokens into an expression, either an atom or a tuple of expressions.'
    # shunting yard algorithm, adapted for expressions
    res = []
    ops = []
    def apply_fun(fun):
        try:
            argc = len(literals[fun]) - 1
            args = ()
            for i in argc:
                args = (res.pop(),) + args
            res.append((fun,) + args)
            return True
        except:
            return False
    for t in tokens:
        if t in atoms():
            res.append(t)
        elif t in functions() or t == '(':
            ops.append(t)
        elif t in operators:
            while ops and precedes(ops[-1], t):
                if not apply_fun(ops.pop()):
                    return None
            ops.append(t)
        elif t == ')':
            while ops and ops[-1] != '(':
                if not apply_fun(ops.pop()):
                    return None
            if not ops:
                return None
            ops.pop()
            if ops and ops[-1] in functions():
                if not apply_fun(ops.pop()):
                    return None
    while ops:
        if ops[-1] in ['(', ')']:
            return None
        apply_fun(ops.pop())
    if len(res) != 1:
        return None
    return res[0]

def output(expr):
    'Convert expression into a readable string representation.'
    pass

# memoize
def precedes(op1, op2):
    'Return whether op1 has higher precedence than op2, or op1 and op2 are left-associative and the same operator.'
    found1 = False
    for op in operators:
        if op == op1:
            found1 = True
        if op == op2:
            return found1
    return False
