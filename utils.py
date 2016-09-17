### Auxiliary utilities

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
         ('=', ('+', '0', 'N'), 'N'),
         ('=', ('+', ('s', 'M'), 'N'),
               ('s', ('+', 'M', 'N'))),
         ('=', ('*', '0', 'N'), '0'),
         ('=', ('*', ('s', 'M'), 'N'),
               ('+', 'N', ('*', 'M', 'N')))]
literals = {True : 'Bool', False : 'Bool',
            'and' : ('Bool', 'Bool', 'Bool'), 'or' : ('Bool', 'Bool', 'Bool'), 'implies' : ('Bool', 'Bool', 'Bool'),
            '=' : ('Bool', True, True), # TODO later modify this using type variables
            '0' : 'Nat', 's' : ('Nat', 'Nat'), '+' : ('Nat', 'Nat', 'Nat'), '*' : ('Nat', 'Nat', 'Nat')}

def predicates():
    'Generate each function that returns a Boolean.'
    for lit in literals:
        if isinstance(literals[lit], tuple) and literals[lit][0] == 'Bool':
            yield lit

def is_variable(expr):
    return isinstance(expr, str) and expr[0].isupper()

def variables(expr):
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

# later infer this from type constructors
def induct(stmt, var):
    'Convert statement into conjunction by inducting on variable.'
    return ('and', evaluate(stmt, {var : '0'}), 
                   ('implies', stmt, evaluate(stmt, {var : ('s', var)})))

# TODO also allow for lazy expansion, e.g. 1 matches (s 0)
def matches(expr1, expr2, typ = True):
    'Check if expr1 subsumes expr2, assuming neither are badly typed, and if so return dictionary of bindings.'
    binds = {}
    stack = [(expr1, expr2, typ)] # check if expr1 matches expr2 and is constrained to type True
    vartypes = {} # types each variable is constrained to
    
    while stack:
        expr1, expr2, typ = stack.pop()
        
        # if the lhs is a literal, the rhs must be the same literal and both must match the type they are constrained to
        if expr1 in literals and not (expr1 == expr2 and subsumes(typ, literals[expr1])):
            return False
        
        if is_variable(expr1):
            # if expr1 is not assigned a type or is assigned an incompatible type
            if expr1 not in vartypes or subsumes(vartypes[expr1], typ): # expr1 is constrained further to typ
                vartypes[expr1] = typ
            elif not subsumes(typ, vartypes[expr1]): # typ doesn't contain expr1
                return False
            
            if expr1 not in binds:
                if expr1 != expr2 and subsumes(vartypes[expr1], get_type(expr2)):
                    binds[expr1] = expr2
            elif binds[expr1] != expr2:
                return False
        
        if isinstance(expr1, tuple):
            if not isinstance(expr2, tuple) or len(expr1) != len(expr2): # mismatched arguments
                return False
            # bind each pair of arguments to the literals they are constrained to based on the type of expr1[0]
            stack += zip(expr1, expr2, (literals[expr1[0]],) + literals[expr1[0]][1:])
    
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

def get_type(expr):
    'Return the type a literal value or application is supposed to have, without verifying.'
    try:
        return literals[expr[0]][0] if isinstance(expr, tuple) else literals[expr]
    except KeyError:
        return False
