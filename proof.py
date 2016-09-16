### Theorem proving on the Peano axioms

# The theorem proving algorithm operates on expressions comprised of literals and universally quantified variables.
# A statement is proven by a series of transformations that ends in the literal True.
# For example, the proof that addition, defined as in the Peano axioms, is associative, is rpresented by these transformations:
# - ('=', ('+', 'M', ('+', 'N', 'K')), ('+', ('+', 'M', 'N'), 'K')) # statement of hypothesis
# - ('and', ('=', ('+', 0, ('+', 'N', 'K')), ('+', ('+', 0, 'N'), 'K')),
#           ('implies', ('=', ('+', 'M', ('+', 'N', 'K')), ('+', ('+', 'M', 'N'), 'K')),
#                       ('=', ('+', ('s', 'M'), ('+', 'N', 'K')), ('+', ('+', ('s', 'M'), 'N'), 'K')))) # induction on M
# - ('and', ('=', ('+', 'N', 'K'), ('+', 'N', 'K')),
#           ('implies', ('=', ('+', 'M', ('+', 'N', 'K')), ('+', ('+', 'M', 'N'), 'K')),
#                       ('=', ('s', ('+', 'M', ('+', 'N', 'K'))), ('s', ('+', ('+', 'M', 'N'), 'K'))))) # definitions of +
# - ('and', True,
#           ('implies', ('=', ('+', 'M', ('+', 'N', 'K')), ('+', ('+', 'M', 'N'), 'K')),
#                       ('=', ('s', ('+', 'M', ('+', 'N', 'K'))), ('s', ('+', ('+', 'M', 'N'), 'K'))))) # equality
# - ('and', True, 
#           ('implies', ('=', ('+', 'M', ('+', 'N', 'K')), ('+', ('+', 'M', 'N'), 'K')),
#                       ('=', ('s', ('+', 'M', ('+', 'N', 'K'))), ('s', ('+', 'M', ('+', 'N', 'K'))))) # application of antecedent
# - ('and', True, ('implies', ('=', ('+', 'M', ('+', 'N', 'K')), ('+', ('+', 'M', 'N'), 'K')), True) # equality
# - ('and', True, True) # truth of implication
# - True # truth of conjunction

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
        if current in preds.values() or current is False:
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
            if next_stmt != current: # quick hack, should instead be in applicable_rules
                new_dist = dists[current] + distance(current, next_stmt)
                if next_stmt not in dists or new_dist < dists[next_stmt]:
                    preds[next_stmt] = rule, current
                    dists[next_stmt] = new_dist
                    heappush(to_visit, (new_dist + epsilon * estimate_cost(next_stmt), next_stmt))
    
    return None

# streamline and generalize these references to specific predicates
def applicable_rules(stmt, typ = True):
    'Generate new statements that can be derived from stmt by the application of a rule.'
    global rules
    
    # if there is a rule that stmt matches (also consider conjunctions), yield that and True
    for rule in rules:
        if matches(rule, stmt):
            yield rule, True
            return
    
    for rule in rules:
        # if rule is an equation, check if either side matches stmt
        if isinstance(rule, tuple) and rule[0] == '=':
            binds = matches(rule[1], stmt, typ)
            if binds:
                yield rule, evaluate(rule[2], binds)
            binds = matches(rule[2], stmt, typ)
            if binds:
                yield rule, evaluate(rule[1], binds)
        
        # if rule is an implication, check if the consequent matches stmt
        if isinstance(rule, tuple) and rule[0] == 'implies':
            binds = matches(rule[2], stmt, typ)
            if binds:
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
            for var in variables(stmt):
                yield var, induct(stmt, var)
