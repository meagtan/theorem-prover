## Auxiliary utilities

def applicable_rules(stmt):
    'Generate new statements that can be derived from stmt by the application of a rule.'
    global rules
    for rule in rules:
        # if there is a rule that stmt matches (also consider conjunctions), yield that and True
        if matches(rule, stmt):
            yield rule, True
            return
        
        # if rule is an equation, check if either side matches stmt
        if isinstance(rule, list) and rule[0] == '=':
            binds = matches(rule[1], stmt)
            if binds:
                yield rule, evaluate(rule[2], binds)
            binds = matches(rule[2], stmt)
            if binds:
                yield rule, evaluate(rule[1], binds)
    # also look for substitutions on each subexpression of stmt
    if isinstance(stmt, list):
        for i in xrange(1, len(stmt)):
            for rule, res in applicable_rules(stmt[i]):
                yield rule, stmt[:i] + res + stmt[i+1:]
    # then apply induction to each variable for predicates
    if is_predicate(stmt):
        for var in variables(stmt):
            yield var, induct(stmt, var)

def estimate_cost(expr):
    'Measure the edit distance of expression to a literal.'
    pass

def distance(expr1, expr2):
    'Measure the edit distance between two expressions.'
    pass

def add_rule(stmt):
    'Add statement to rules.'
    global rules
    rules.append(stmt)

# by convention, variables are capital letters
rules = [['=', ['+', 0, 'N'], 'N'],
         ['=', ['+', ['s', 'M'], 'N'],
               ['s', ['+', 'M', 'N']]],
         ['=', ['*', 0, 'N'], 0],
         ['=', ['*', ['s', 'M'], 'N'],
               ['+', 'N', ['*', 'M', 'N']]]]
literals = [True, False, 'and', '=', 0, 's', '+', '*']

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

def evaluate(expr, binds = None):
    "Evaluate expr using the given bindings for variables, assumed to be valid."
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