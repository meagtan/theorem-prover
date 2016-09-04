## Auxiliary utilities

# by convention, variables are capital letters
rules = [['=', ['+', 0, 'N'], 'N'],
         ['=', ['+', ['s', 'M'], 'N'],
               ['s', ['+', 'M', 'N']]],
         ['=', ['*', 0, 'N'], 0],
         ['=', ['*', ['s', 'M'], 'N'],
               ['+', 'N', ['*', 'M', 'N']]]]
literals = [True, False, 'and', '=', 'implies', 0, 's', '+', '*']
predicates = ['and', '=', 'implies']

def is_variable(expr):
    return isinstance(expr, str) and len(expr) == 1 and expr.isupper()

def variables(expr):
    global literals
    res = []
    stack = [expr]
    while stack:
        current = stack.pop()
        if is_variable(current) and current not in res:
            res.append(current)
        if isinstance(current, list):
            stack += current
    return res

def induct(stmt, var):
    'Convert statement into conjunction by inducting on variable.'
    return ['and', evaluate(stmt, {var : 0}), 
                   ['implies', stmt, evaluate(stmt, {var : ['s', var]})]]

# also allow for lazy expansion, e.g. 1 matches (s 0)
def matches(expr1, expr2, binds = None):
    'Check if expr1 subsumes expr2, and if so return dictionary of bindings.'
    global literals
    if binds is None:
        binds = {}
    stack = [(expr1, expr2)]
    while stack:
        expr1, expr2 = stack.pop()
        if expr1 in literals and expr1 != expr2:
            return None
        if is_variable(expr1):
            if expr1 not in binds:
                binds[expr1] = expr2
            elif binds[expr1] == expr2:
                return None
        if not isinstance(expr2, list) or len(expr1) != len(expr2):
            return None
        stack += zip(expr1, expr2)
    return binds

def evaluate(expr, binds = None):
    "Evaluate expr using the given bindings for variables, assumed to be valid."
    global literals
    if binds is None:
        binds = {}
    if expr in literals:
        return expr
    if is_variable(expr):
        if expr in binds:
            return binds[expr]
        else:
            return expr
    return map(lambda e: evaluate(e, binds), expr)

def deep_length(expr):
    'Return the number of atoms in an expression.'
    res = 0
    stack = [expr]
    while stack:
        expr = stack.pop()
        if isinstance(expr, list):
            stack += expr
        else:
            res += 1
    return res