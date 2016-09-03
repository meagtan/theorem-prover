## Auxiliary utilities

def applicable_rules(stmt):
    'Generate new statements that can be derived from stmt by the application of a rule.'
    global rules
    global predicates
    
    # if there is a rule that stmt matches (also consider conjunctions), yield that and True
    for rule in rules:
        if matches(rule, stmt):
            yield rule, True
            return
    
    for rule in rules:
        # if rule is an equation, check if either side matches stmt
        if isinstance(rule, list) and rule[0] == '=':
            binds = matches(rule[1], stmt)
            if binds:
                yield rule, evaluate(rule[2], binds)
            binds = matches(rule[2], stmt)
            if binds:
                yield rule, evaluate(rule[1], binds)
        
        # if rule is an implication, check if the consequent matches stmt
        if isinstance(rule, list) and rule[0] == 'implies':
            binds = matches(rule[2], stmt)
            if binds:
                yield rule, evaluate(rule[1], binds)
    
    # also look for substitutions on each subexpression of stmt
    if isinstance(stmt, list):
        # This should not apply to the consequent of an implication, for a => b does not convert c => b into c => a, but
        #  vice versa. Instead, the antecedent should be able to apply to the consequent.
        for i in xrange(1, len(stmt)):
            for rule, res in applicable_rules(stmt[i]):
                yield rule, stmt[:i] + res + stmt[i+1:] # here check for True arguments in conjunction
        
        # then apply induction to each variable for predicates
        if stmt[0] in predicates:
            for var in variables(stmt):
                yield var, induct(stmt, var)

def estimate_cost(expr):
    'Measure the complexity of the given expression, returning 0 for a literal.'
    # can measure length, depth, number of free variables
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