## Distance

def estimate_cost(expr):
    'Measure the complexity of the given expression, returning 0 for a literal.'
    # TODO can measure length, depth, number of free variables
    # Make sure the heuristic is consistent with distance()
    pass

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
        d = {}
        
        for i in xrange(m):
            d[i, 0] = distance(expr1[i], expr2[0])
        for j in xrange(n):
            d[0, j] = distance(expr1[0], expr2[j])
        
        for j in xrange(n):
            for i in xrange(m):
                if expr1[i] == expr2[j]:
                    d[i, j] = d[i - 1, j - 1]
                else:
                    d[i, j] = min(d[i - 1, j]     + deep_length(expr1[i]),        # delete expr1[i]
                                  d[i,     j - 1] + deep_length(expr2[j]),        # insert expr2[j]
                                  d[i - 1, j - 1] + distance(expr1[i], expr2[j])) # substitute expr2[j] for expr1[i]
        return d[m - 1, n - 1]
            
    # If both arguments are lists, they are compared by the usual Levenshtein distance, except the cost of deletion or insertion
    #  is equal to the deep length of the item deleted and the cost of substitution is the distance of the elements substituted.
    if isinstance(expr1, list) and isinstance(expr2, list):
        return list_distance(expr1, expr2)
    
    # Else, if at least one argument is an atom, the distance is the deep length of the other argument, 
    #  possibly minus one for the case of the former being contained inside the latter
    if isinstance(expr1, list):
        expr2, expr1 = expr1, expr2
    return deep_length(expr2) - (expr1 in flatten(expr2))

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
    return isinstance(expr, str) and expr[0].isupper()

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
    return len(flatten(expr))

def flatten(expr):
    'Return the list of atoms in an expression.'
    res = []
    stack = [expr]
    
    while stack:
        expr = stack.pop()
        if isinstance(expr, list):
            stack += expr
        else:
            res.append(expr)
    
    return res