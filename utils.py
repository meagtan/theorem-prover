## Additional utilities

# by convention, variables are capital letters
rules = [['=', ['+', 0, 'N'], 'N'],
         ['=', ['+', ['s', 'M'], 'N'],
               ['s', ['+', 'M', 'N']]],
         ['=', ['*', 0, 'N'], 0],
         ['=', ['*', ['s', 'M'], 'N'],
               ['+', 'N', ['*', 'M', 'N']]]]
literals = ['=', 0, 's', '+', '*', 'and']

def is_variable(expr):
    return isinstance(expr, str) and len(expr) == 1 and expr.isupper()

# also allow for lazy expansion, e.g. 1 matches (s 0)
def matches(expr1, expr2, binds = {}):
    'Check if expr1 subsumes expr2, and if so return dictionary of bindings.'
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

def add_rule(stmt):
    global rules
    rules.append(stmt)

def applicable_rules(stmt):
    'Generate new statements that can be derived from stmt by the application of a rule.'
    global rules
    pass