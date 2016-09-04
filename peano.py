### Theorem proving based on the Peano axioms

import heapq
from utils import *

## Proof algorithm

def prove(stmt, epsilon = 1):
    'Search a proof or disproof for statement in environment using heuristic search.'
    to_visit  = []
    preds = {} # This map and the one below could be implemented as a trie
    dists = {}
    dists[stmt] = 0
    
    heappush(to_visit, (0, stmt))
    
    # This loop might not terminate for axiomatic systems complex enough, add conditions
    while to_visit: 
        current = heappop(to_visit)[1]
        
        # current already visited
        if current in preds.values():
            continue
        
        # found conclusion, end search and construct proof from preds
        # for every rule in env, applicable_rules generates an evaluation rule converting
        #  that rule to true
        if current is True:
            rules.append(stmt)
            path = []
            while current in preds:
                path.append((preds[current][0], current))
                current = preds[current][1]
            path.append(expr)
            return True, path.reverse()
        
        for rule, next_stmt in applicable_rules(current):
            new_dist = dists[current] + distance(current, next_stmt)
            if next_stmt not in dists or new_dist < dists[next_stmt]:
                preds[next_stmt] = rule, current
                dists[next_stmt] = new_dist
                heappush(to_visit, (new_dist + epsilon * estimate_cost(next_stmt), next_stmt))
    
    return None

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
        # TODO This should not apply to the consequent of an implication, for a => b does not convert c => b into c => a, but
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
    # TODO can measure length, depth, number of free variables
    pass

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
        m, n = len(expr1) + 1, len(expr2) + 1
        # create 2d array
        d = [[0 for j in xrange(m)] for i in xrange(n)]
        
        # distances to the empty string (TODO there is no empty expression, instead start from the first atom)
        for i in xrange(1, m):
            d[i][0] = deep_length(expr1[:i])
        for j in xrange(1, n):
            d[j][0] = deep_length(expr2[:j])
        
        for j in xrange(1, n):
            for i in xrange(1, m):
                if expr1[i-1] == expr2[j-1]:
                    d[i][j] = d[i-1][j-1]
                else:
                    d[i][j] = min(d[i-1][j]   + deep_length(expr1[i-1]),          # delete expr1[i-1]
                                  d[i][j-1]   + deep_length(expr2[j-1]),          # insert expr2[j-1]
                                  d[i-1][j-1] + distance(expr1[i-1], expr2[j-1])) # substitute expr2[j-1] for expr1[i-1]
        
        return d[m-1][n-1]
            
    # If both arguments are lists, they are compared by the usual Levenshtein distance, except the cost of deletion or insertion
    #  is equal to the deep length of the item deleted and the cost of substitution is the distance of the elements substituted.
    # Else, if at least one argument is an atom, 
    pass