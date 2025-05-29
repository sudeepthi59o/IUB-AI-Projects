#!/usr/local/bin/python3
# solve_fairies.py : Fairy puzzle solver
#
# Code by: Frangil Ramirez Koteich (fraramir), Pranay Chowdary Namburi (pnambur), Sudeepthi Rebbalapalli (surebbal)
#
# Based on skeleton code by B551 course staff, Fall 2023
#
# N fairies stand in a row on a wire, each adorned with a magical symbol from 1 to N.
# In a single step, two adjacent fairies can swap places. How can
# they rearrange themselves to be in order from 1 to N in the fewest
# possible steps?

# !/usr/bin/env python3
import sys
from queue import PriorityQueue as PQ
from bisect import bisect, insort


N=5

#####
# THE ABSTRACTION:
#
# Initial state:

# Goal state:
# given a state, returns True or False to indicate if it is the goal state
def is_goal(state):
    return state == list(range(1, N+1))

# Successor function:
# given a state, return a list of successor states
def successors(state):
    return [ state[0:n] + [state[n+1],] + [state[n],] + state[n+2:] for n in range(0, N-1) ]


# Heuristic function:
# given a state, count the number of inversion pairs. 
# algorithm seen in Algorithm Design Course CSCI-B503.
# algorithm from : "Algorithm Design" by Eva Tardos and Jon Kleinberg, ISBN 0-321-29535-8 
#                  Pages 221-225. 
# implementation of algorithm adapted from: https://www.geeksforgeeks.org/inversion-count-in-array-using-merge-sort/
# 
def h(state):
    L = len(state)
    if L <= 1:
        return 0
    
    # initialize priority queue to be empty
    sortList = PQ()
    result = 0
 
    for i, v in enumerate(state):
        sortList.put((v, i))
 
    # Create a sorted list of indexes
    x = []
    while not sortList.empty():
       
        v, i = sortList.get()
         
        # Find the current minimum's index
        # the index y can represent how many minimums on the left
        y = bisect(x, i)
         
        # i can represent how many elements on the left
        # i - y can find how many bigger nums on the left
        result += i - y
 
        insort(x, i)
 
    return result
# end of adapted code

def g(statePath):
    return len(statePath) 

def f(state, path):
    return h(state) + g(path)

#########
#
# THE ALGORITHM:
#
# A* implementation. 
#
def solve(initial_state):
    # Initialize number of nodes created and expanded (just a metric)
    nodes_expanded = 0
    nodes_created = 0

    # initialize priority queue to be empty
    # each element in priority queue is a tuple = (cost, (state, path))
    fringe = PQ()

    fringe.put((f(initial_state, []), (initial_state, [])))
    while not fringe.empty():
        # extract the state and path from the queue
        _, element = fringe.get()
        state = element[0]
        path = element[1]
        
        # increment counter
        nodes_expanded += 1

        if is_goal(state):
            return path+[state,]
        
        # for each successor of state, add to queue as a tuple
        for s in successors(state):
            fringe.put((f(s, path+[state,]), (s, path+[state,])))

            # increment counter
            nodes_created += 1
    
    # if no solution return empty path
    return []

# Please don't modify anything below this line
#
if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected a test case filename"))

    test_cases = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            test_cases.append([ int(i) for i in line.split() ])
    for initial_state in test_cases:
        	print('From state ' + str(initial_state) + " found goal state by taking path: " + str(solve(initial_state)))

    

