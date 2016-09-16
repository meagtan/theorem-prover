## Distance

def estimate_cost(expr):
    'Measure the complexity of the given expression, returning 0 for a literal.'
    if isinstance(expr, tuple):
        if expr[0] == 'and':
            return sum(estimate_cost(e) for e in expr[1:])
        if expr[0] == 'or':
            return min(estimate_cost(e) for e in expr[1:])
        if expr[0] == 'implies':
            return estimate_cost(expr[2]) # only check consequent
        if expr[0] == '=':
            return distance(expr[1], expr[2])
    # The number of variables, deep length - 1 and depth are all consistent heuristics. Which of their linear combinations are?
    return deep_length(expr) - 1 # shortest distance to a literal

# TODO memoize this and distinguish variables from literals
def distance(expr1, expr2):
    '''Measure the edit distance between two expressions, defined based on the following elementary operations:
    - The application of a literal to an expression, e.g. f applied to x is [f, x] and [f, x] applied to y is [f, x, y].
      Both [f, x, y] and [f, [x, y]] can be reached from [f, x] by the application of y.
    - The removal of a literal from the end of a function application, e.g. [f, [x, y]] is converted to either f or [f, x].
    - The substitution of two literals (and perhaps the instantiation of a variable by an expression).
    This distance measure subsumes the Levenshtein distance between two strings, considered as a list of characters, when
    the distance between two characters is either 0 or 1 depending on whether they are the same or not, and the cost of adding
    or removing a character is always 1, which is the deep length of the character, taken as an atom.
    '''
    def list_distance(expr1, expr2):
        'Implementation of the Wagner-Fischer algorithm for the extended tree edit distance.'
        m, n = len(expr1), len(expr2)
        d = {} # stores shortest paths of edits between subexpressions
        l = {} # stores deep length of each subexpression of expr1 and expr2
        
        for i in xrange(m):
            l[1, i] = deep_length(expr1[i])
            d[i, 0] = distance(expr1[i], expr2[0])
        for j in xrange(n):
            l[2, j] = deep_length(expr2[j])
            d[0, j] = distance(expr1[0], expr2[j])
        
        for j in xrange(1, n):
            for i in xrange(1, m):
                if expr1[i] == expr2[j]:
                    d[i, j] = d[i-1, j-1]
                else:
                    d[i, j] = min(d[i-1, j]   + l[1, i],                      # delete expr1[i]
                                  d[i,   j-1] + l[2, j],                      # insert expr2[j]
                                  d[i-1, j-1] + distance(expr1[i], expr2[j])) # substitute expr2[j] for expr1[i]
        return d[m-1, n-1]
            
    # If both arguments are lists, they are compared by the usual Levenshtein distance, except the cost of deletion or insertion
    #  is equal to the deep length of the item deleted and the cost of substitution is the distance of the elements substituted.
    if isinstance(expr1, tuple) and isinstance(expr2, tuple):
        # simplify and generalize
        if expr1[0] == 'and':
            if expr2[0] == 'and':
                return min(distance(expr1[1], expr2[1]), distance(expr1[2], expr2[1]))
            return sum(distance(e, expr2) for e in expr1[1:])
        if expr2[0] == 'and':
            return sum(distance(expr1, e) for e in expr2[1:])
        if expr1[0] == 'or':
            return min(distance(e, expr2) for e in expr1[1:])
        if expr2[0] == 'or':
            return min(distance(expr1, e) for e in expr2[1:])
        # quick solution: only check consequent in implication
        if expr1[0] == 'implies':
            return distance(expr1[2], expr2)
        if expr2[0] == 'implies':
            return distance(expr1, expr2[2])
        
        return list_distance(expr1, expr2)
    
    # Else, if at least one argument is an atom, the distance is the deep length of the other argument, 
    #  possibly minus one for the case of the former being contained inside the latter
    if isinstance(expr1, tuple):
        expr2, expr1 = expr1, expr2
    return deep_length(expr2) - (expr1 in flatten(expr2))

## Auxiliary utilities

# by convention, variables are capital letters
rules = [True,
         ('=', 'X', 'X'), 
         ('=', ('=', 'X', 'Y'), ('=', 'Y', 'X')),
         ('implies', ('=', 'P', 'Q'), ('implies', 'P', 'Q')), # should this be necessary?
         ('implies', ('and', ('=', 'X', 'Y'), ('=', 'Y', 'Z')),
                     ('=', 'X', 'Z')),
         ('=', ('=', ('s', 'M'), ('s', 'N')),
               ('=', 'M', 'N')),
         ('and', True, True),
         ('implies', 'P', True),
         ('implies', False, 'P'),
         ('implies', 'P', 'P'),
         ('=', ('+', 0, 'N'), 'N'),
         ('=', ('+', ('s', 'M'), 'N'),
               ('s', ('+', 'M', 'N'))),
         ('=', ('*', 0, 'N'), 0),
         ('=', ('*', ('s', 'M'), 'N'),
               ('+', 'N', ('*', 'M', 'N')))]
literals = [True, False, 'and', 'or', 'implies', '=', 0, 's', '+', '*']
predicates = ['and', 'or', '=', 'implies']
types = {True : 'Bool', False : 'Bool',
         'and' : ('Bool', 'Bool', 'Bool'), 'or' : ('Bool', 'Bool', 'Bool'), 'implies' : ('Bool', 'Bool', 'Bool'),
         '=' : ('Bool', True, True),
         0 : 'Nat', 's' : ('Nat', 'Nat'), '+' : ('Nat', 'Nat', 'Nat'), '*' : ('Nat', 'Nat', 'Nat')}

def is_variable(expr):
    return isinstance(expr, str) and expr[0].isupper()

def variables(expr):
    global literals
    res = []
    stack = [expr]
    
    while stack:
        current = stack.pop()
        if is_variable(current) and current not in res:
            res.append(current)
        if isinstance(current, tuple):
            stack += current
    
    res.reverse()
    return res

def induct(stmt, var):
    'Convert statement into conjunction by inducting on variable.'
    return ('and', evaluate(stmt, {var : 0}), 
                   ('implies', stmt, evaluate(stmt, {var : ('s', var)})))

# TODO also allow for lazy expansion, e.g. 1 matches (s 0)
def matches(expr1, expr2, binds = None):
    'Check if expr1 subsumes expr2, and if so return dictionary of bindings.'
    global literals
    if binds is None:
        binds = {}
    stack = [(expr1, expr2)]
    
    while stack:
        expr1, expr2 = stack.pop()
        if expr1 in literals and expr1 != expr2:
                return False
        if is_variable(expr1):
            if expr1 not in binds:
                if expr1 != expr2:
                    binds[expr1] = expr2
            elif binds[expr1] != expr2:
                return False
        if isinstance(expr1, tuple):
            if not isinstance(expr2, tuple) or len(expr1) != len(expr2):
                return False
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
    
    return tuple(map(lambda e: evaluate(e, binds), expr))

def deep_length(expr):
    'Return the number of atoms in an expression.'
    return len(flatten(expr))

def flatten(expr):
    'Return the list of atoms in an expression.'
    res = []
    stack = [expr]
    
    while stack:
        expr = stack.pop()
        if isinstance(expr, tuple):
            stack += expr
        else:
            res.append(expr)
    
    res.reverse()
    return res

# TODO include inheritance later
def subsumes(type1, type2):
    'Return true if type2 is contained in type1.'
    return type1 is True or type1 == type2
