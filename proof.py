### Theorem proving on the Peano axioms

import heapq as hp
from utils import *

## Proof algorithm

# estims memoizes heuristics and updates them through landmarks
# since default arguments refer to one object, the memoization will be carried over across multiple calls to proof
def prove(stmt, epsilon = 1, estims = {}): 
    'Search a proof or disproof for statement in environment using heuristic search.'
    
    # Auxiliary memoization functions
    def get_cost(s):
        'Return estimated cost of statement memoized.'
        if s not in estims:
            estims[s] = estimate_cost(s)
        return estims[s]
    def update_cost(s, other):
        'Set new estimated cost of statement to maximum of current estimate and other estimate.'
        estims[s] = max(get_cost(s), other)
        return estims[s]
        
    # Main algorithm
    
    to_visit = []
    preds = {}
    dists = {}
    dists[stmt] = 0
    
    hp.heappush(to_visit, (0, stmt))
    
    # This loop might not terminate for axiomatic systems complex enough, add conditions
    while to_visit: 
        current = hp.heappop(to_visit)[1]
        
        # current already visited or dead end
        if current in preds.values() or current is False:
            continue
        
        # found conclusion, end search and construct proof from preds
        # for every rule in env, applicable_rules generates an evaluation rule converting that rule to true
        if current is True:
            rules.append(stmt)
            
            # update estims with stmt as landmark using the triangle inequality
            for node in dists:
                # each node in dists is also in estims, since they are both defined when node is first added to the heap
                update_cost(node, dists[current] - dists[node])
            
            # construct path
            path = []
            while current in preds:
                path.append((preds[current][0], current))
                current = preds[current][1]
            path.append(expr)
            return True, path.reverse()
        
        for rule, next_stmt in applicable_rules(current):
            if next_stmt != current: # quick hack, should instead be in applicable_rules
                new_dist = dists[current] + distance(current, next_stmt)
                if next_stmt not in dists or new_dist < dists[next_stmt]:
                    preds[next_stmt] = rule, current
                    dists[next_stmt] = new_dist
                    hp.heappush(to_visit, (new_dist + epsilon * get_cost(next_stmt), next_stmt))
    
    return None

# streamline and generalize these references to specific predicates
def applicable_rules(stmt, typ = True):
    'Generate new statements that can be derived from stmt by the application of a rule.'
    global rules
    
    # if there is a rule that stmt matches (also consider conjunctions), yield that and True
    for rule in rules:
        if matches(rule, stmt, typ):
            yield rule, True
            return
    
    for rule in rules:
        # if rule is an equation, check if either side matches stmt
        if isinstance(rule, tuple) and rule[0] == '=':
            binds = matches(rule[1], stmt, typ)
            if binds is not False: # matches can also return {} as a valid set of bindings
                yield rule, evaluate(rule[2], binds)
            binds = matches(rule[2], stmt, typ)
            if binds is not False:
                yield rule, evaluate(rule[1], binds)
        
        # if rule is an implication, check if the consequent matches stmt
        if isinstance(rule, tuple) and rule[0] == 'implies' and get_type(stmt) == typ == 'Bool': # get_type('implies')[1]
            binds = matches(rule[2], stmt, typ)
            if binds is not False:
                yield rule, evaluate(rule[1], binds)
    
    # also look for substitutions on each subexpression of stmt
    if isinstance(stmt, tuple):
        # implications must preserve variable bindings
        # the antecedent can be made to apply to the consequent, but that doesn't affix the binding of its variables
        if stmt[0] != 'implies':
            for i in xrange(1, len(stmt)):
                for rule, res in applicable_rules(stmt[i], types[stmt[0]][i]):
                    yield rule, stmt[:i] + (res,) + stmt[i+1:] # here check for True arguments in conjunction
        
        # then apply induction to each variable for predicates
        if stmt[0] in predicates():
            for var, typ in variables(stmt):
                ind = induct(stmt, var, typ)
                if ind is not None:
                    yield var, ind

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
