#!/usr/local/bin/python3
# solver2023.py : 2023 Sliding tile puzzle solver
#
# Code by: Frangil Ramirez Koteich (fraramir), Pranay Chowdary Namburi (pnambur), Sudeepthi Rebbalapalli (surebbal)
#
# Based on skeleton code by B551 Staff, Fall 2023
#

import sys
from bisect import bisect, insort
#import queue
from queue import PriorityQueue as PQ
import numpy as np
from dataclasses import dataclass, field
from typing import Any 

ROWS=5
COLS=5

# create class used to wrap data before pushing it into queue
# class adapted from: https://docs.python.org/3/library/queue.html?highlight=priorityqueue#queue.PriorityQueue
@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)
    def __getitem__(self, item):
         return self.item
# end of adapted code

# Successor function: 
# return a list of possible successor states
def successors(state):
    states = []
    for i in range(ROWS):
        # Rotate each row right
        curr_state = state.copy()
        curr_state[i] = np.roll(curr_state[i], 1)
        states.append((curr_state, "R"+str(i + 1)))

        # Rotate each row left
        curr_state = state.copy()
        curr_state[i] = np.roll(curr_state[i], -1)
        states.append((curr_state, "L"+str(i + 1)))

        # Rotate each column up
        curr_state = state.copy()
        curr_state[:, i] = np.roll(curr_state[:, i], shift = -1)
        states.append((curr_state, "U"+str(i + 1)))

        # Rotate each column down
        curr_state = state.copy()
        curr_state[:, i] = np.roll(curr_state[:, i], shift = 1)
        states.append((curr_state, "D"+str(i + 1)))
    
    # Rotate Outer cells clockwise (Oc)
    curr_state = state.copy()
    t = curr_state[0][0]
    for i in range(ROWS - 1):
        curr_state[i][0] = curr_state[i + 1][0]
    for i in range(COLS - 1):
        curr_state[-1][i] = curr_state[-1][i + 1]
    for i in range((ROWS - 1), 0, -1):
        curr_state[i][COLS - 1] = curr_state[i - 1][COLS - 1]
    for i in range((COLS - 1), 1, -1):
        curr_state[0][i] = curr_state[0][i - 1]
    curr_state[0][1] = t
    states.append((curr_state, "Oc"))

    # Rotate Outer cells counter clockwise (Occ)
    curr_state = state.copy()
    t = curr_state[0][0]
    for i in range(COLS - 1):
        curr_state[0][i] = curr_state[0][i + 1]
    for i in range(ROWS - 1):
        curr_state[i][COLS - 1] = curr_state[i + 1][COLS - 1]
    for i in range((COLS - 1), 0, -1):
        curr_state[ROWS - 1][i] = curr_state[ROWS - 1][i - 1]
    for i in range((ROWS - 1), 1, -1):
        curr_state[i][0] = curr_state[i - 1][0]
    curr_state[1][0] = t
    states.append((curr_state, "Occ"))

    # Rotate Inner cells clockwise (Ic)
    curr_state = state.copy()
    t = curr_state[1][1]
    for i in range(1, ROWS - 2):
        curr_state[i][1] = curr_state[i + 1][1]
    for i in range(1, COLS - 2):
        curr_state[-2][i] = curr_state[-2][i + 1]
    for i in range((ROWS - 2), 1, -1):
        curr_state[i][COLS - 2] = curr_state[i - 1][COLS - 2]
    for i in range((COLS - 2), 2, -1):
        curr_state[1][i] = curr_state[1][i - 1]
    curr_state[1][2] = t
    states.append((curr_state, "Ic"))

    # Rotate Inner cells counter clockwise (Icc)
    curr_state = state.copy()
    t = curr_state[1][1]
    for i in range(1, COLS - 2):
        curr_state[1][i] = curr_state[1][i + 1]
    for i in range(1, ROWS - 2):
        curr_state[i][COLS - 2] = curr_state[i + 1][COLS - 2]
    for i in range((COLS - 2), 1, -1):
        curr_state[ROWS - 2][i] = curr_state[ROWS - 2][i - 1]
    for i in range((ROWS - 2), 2, -1):
        curr_state[i][1] = curr_state[i - 1][1]
    curr_state[2][1] = t
    states.append((curr_state, "Icc"))
    
    return states

# Inversion counter function:
# given a 1D array, count the number of inversion pairs. 
# algorithm seen in Algorithm Design Course CSCI-B503.
# algorithm from : "Algorithm Design" by Eva Tardos and Jon Kleinberg, ISBN 0-321-29535-8 
#                  Pages 221-225. 
# implementation of algorithm adapted from: https://www.geeksforgeeks.org/inversion-count-in-array-using-merge-sort/
# 
def count_inversions(lyst):
    
    # initialize priority queue to be empty
    sortList = PQ()
    result = 0
 
    for i, v in enumerate(lyst):
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

# Heuristic function:
# for every state (5x5 matrix), count inversions on each row and column
def h(state):

    r = 0
    c = 0
    heuristic = 0
    cols = np.array([0, 0, 0, 0, 0])
    
    # count inversions on each row
    for r in range(len(state)):
        heuristic += count_inversions(state[r])
    r=0
    
    # count inversions on each column
    for r in range(len(state)):
        for c in range(len([state][0])):
            cols[c] = state[c][r]
        heuristic += count_inversions(cols)

    # return heuristic // 4 works almost identically (see README file)
    return heuristic / 3.15

def g(statePath):
    return len(statePath) 

def f(state, path):
    return h(state) + g(path)

def printable_board(board):
    return [ ('%3d ')*COLS  % board[j:(j+COLS)] for j in range(0, ROWS*COLS, COLS) ]


# check if we've reached the goal
def is_goal(state):
    solution =  np.array([[1,2,3,4,5], [6,7,8,9,10], [11,12,13,14,15], [16,17,18,19,20], [21,22,23,24,25]])
    if np.array_equal(solution, state):
        return True
    
    return False

def solve(initial_board):
    """
    1. This function should return the solution as instructed in assignment, consisting of a list of moves like ["R2","D2","U1"].
    2. Do not add any extra parameters to the solve() function, or it will break our grading and testing code.
       For testing we will call this function with single argument(initial_board) and it should return 
       the solution.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    # Convert input tuple to 5x5 matrix
    matrixBoard = np.reshape(initial_board, (5, 5))
    
    # initialize priority queue to be empty
    # each element in priority queue is a tuple = (cost, (state, path))
    fringe = PQ()
    nodes = 0

    # initialize node counter (just a metric)
    expanded = 0

    # initilize list of visited nodes to be empty
    # only use if doing graph search
    visited = []

    fringe.put((f(matrixBoard, []), (matrixBoard, [])))

    while not fringe.empty():
        i=0

        # boolean flag to determine whether to add state to queue or not
        # in graph search, if node has been visited then do not add to queue again
        # and do not look at its successors
        past = 1
        element = fringe.get()
        expanded += 1

        state = element[1][0]
        path = element[1][1]
        if is_goal(state):
            print("Nodes expanded: %-16d Nodes created: %-16d Path lenght: %-4d" %  (expanded, nodes, len(path)))
            print('\a')
            return path
        
        # if doing tree search, comment for loop below       
        for i in range(len(visited)):
            if np.array_equal(state,visited[i]):
                past = 0
                break;
        if past:
            visited.append(state)
        # if tree search, comment up to this line

        # if tree search, un-nest this for loop from the one above
        # and do NOT comment this loop
            for s in successors(state):
                nodes += 1
                fringe.put(PrioritizedItem(f(s[0], path+[s[1],]), (s[0], path+[s[1],])))
        
        # print metrics
        if (expanded % 1000 == 0):
            print("Nodes expanded: %-16d Nodes created: %-16d Path lenght: %-4d" %  (expanded, nodes, len(path)))

    # if no solution then return empty path
    return []

# Please don't modify anything below this line
#
if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected a board filename"))

    start_state = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            start_state += [ int(i) for i in line.split() ]

    if len(start_state) != ROWS*COLS:
        raise(Exception("Error: couldn't parse start state file"))

    print("Start state: \n" +"\n".join(printable_board(tuple(start_state))))

    print("Solving...")
    route = solve(tuple(start_state))
    
    print("Solution found in " + str(len(route)) + " moves:" + "\n" + " ".join(route))