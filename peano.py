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
    
    heapq.heappush(to_visit, (0, stmt))
    
    # This loop might not terminate for axiomatic systems complex enough, add conditions
    while to_visit: 
        current = heapq.heappop(to_visit)[1]
        
        # current already visited
        if current in preds.values():
            continue
        
        # found conclusion, end search and construct proof from preds
        # for every rule in env, applicable_rules generates an evaluation rule converting
        #  that rule to true
        if current is True:
            add_rule(stmt)
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
                heapq.heappush(to_visit, (new_dist + epsilon * estimate_cost(next_stmt), next_stmt))
    
    return None