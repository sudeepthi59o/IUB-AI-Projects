#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: Frangil Ramirez Koteich (fraramir), Pranay Chowdary Namburi (pnambur), Sudeepthi Rebbalapalli (surebbal)
#
# Based on skeleton code by B551 Course Staff, Fall 2023
#


# !/usr/bin/env python3
import sys
import networkx as nx
from queue import PriorityQueue as PQ
from math import radians, cos, sin, asin, sqrt, tanh

# Goal state:
def is_goal(state,end):
    return state == end

# Successor function:
def successors(G,state):
    return list(n for n in G.neighbors(state))

# Function to build the graph from given datasets using networkx module
def build_graph():
    nodes = []
    with open('city-gps.txt', 'r') as file:
            for line in file: 
                    nodes.append([i for i in line.split() ])

    edges = []
    with open('road-segments.txt', 'r') as file:
            for line in file: 
                    edges.append([i for i in line.split() ])
    
    G=nx.Graph()
    max_speed_limit = 1
    for x in nodes:
       if x:
           G.add_node(x[0],latitude=float(x[1]),longitude=float(x[2]))
    for y in edges:
       if y:
           max_speed_limit = max(max_speed_limit,int(y[3]))
           G.add_edge(y[0],y[1],distance=float(y[2]),limit=float(y[3]),highway=y[4],time=float(y[2])/float(y[3]))
    
    #For nodes with missing latitude and longitude
    for node in G.nodes:
        nodeattributes = G.nodes[node]
        nearest=sorted([(G[n][node]['distance'],n) for n in G.neighbors(node) if ('latitude' in G.nodes[n]) and ('longitude' in G.nodes[n])])
        if nearest:
            attr=G.nodes[nearest[0][1]]
        else:
             lat=lon=0
        if nodeattributes.get('latitude') is None:
                G.nodes[node]['latitude']=attr.get('latitude')
        if nodeattributes.get('longitude') is None:
                G.nodes[node]['longitude']=attr.get('longitude')
    return G, max_speed_limit

# To find the shortest distance between two coordinates. 
# implementation of the formula adapted from: https://www.geeksforgeeks.org/program-distance-two-points-earth/#
def haversine_distance(lat1, lat2, lon1, lon2):
     
    # The math module contains a function named
    # radians which converts from degrees to radians.
    lon1 = radians(lon1)
    lon2 = radians(lon2)
    lat1 = radians(lat1)
    lat2 = radians(lat2)
      
    # Haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
 
    c = 2 * asin(sqrt(a)) 
    return(c * 3976)

# g & h of distance cost function
def h_distance(current_city, destination_city, Graph):
    lat1=Graph.nodes[current_city]['latitude']
    long1=Graph.nodes[current_city]['longitude']
    lat2=Graph.nodes[destination_city]['latitude']
    long2=Graph.nodes[destination_city]['longitude']

    # Shortest Distance using Haversine formula
    # Finding the shortest distance in miles between 2 nodes
    return haversine_distance(lat1, lat2, long1, long2)

def g_distance(route_taken_till_now):
    if(len(route_taken_till_now)):
         return route_taken_till_now[-1][-3]
    return 0

# g & h of segments cost function
def h_segments(current_city, destination_city, Graph):
    return 1

def g_segments(route_taken_till_now):
    return len(route_taken_till_now)

# g & h of time cost function
def h_time(current_city, destination_city, Graph, max_speed_limit):
    return round(h_distance(current_city, destination_city, Graph)/max_speed_limit,5)

def g_time(route_taken_till_now, Graph):
    if(len(route_taken_till_now)):
        return route_taken_till_now[-1][-2]
    return 0

# g & h of delivery cost function
def h_delivery(current_city, destination_city, Graph, max_speed_limit):
    return round(h_distance(current_city, destination_city, Graph)/max_speed_limit,5)

def g_delivery(route_taken_till_now, Graph):
    if(len(route_taken_till_now)):
        return route_taken_till_now[-1][-1]
    return 0

# Common f()
def f(city, destination_city, route_taken_till_now, Graph, cost_type, max_speed_limit = 1):
    if(cost_type.lower() == "distance"):
        return g_distance(route_taken_till_now) + h_distance(city, destination_city, Graph)
    elif(cost_type.lower() == "segments"):
        return g_segments(route_taken_till_now) + h_segments(city, destination_city, Graph)
    elif(cost_type.lower() == "time"):
        return g_time(route_taken_till_now, Graph) + h_time(city, destination_city, Graph, max_speed_limit)
    elif(cost_type.lower() == "delivery"):
        return g_delivery(route_taken_till_now, Graph) + h_delivery(city, destination_city, Graph, max_speed_limit)

    return 0

def get_route(start, end, cost):

    fringe = PQ()
    
    # Build graph from the given datasets
    G, max_speed_limit = build_graph()

    # each element in priority queue contains a tuple = (heuristic_cost(current_city, destination, route_takenß, Graph, cost_type), (state, route_taken))
    fringe.put((f(start, end, [], G, cost), (start, [])))

    # Keep a track of visited cities
    visited = {}

    while not fringe.empty():
        element = fringe.get()
        current_city = element[1][0]
        route_taken_till_now = element[1][1]

        if(current_city in visited and visited[current_city] <= element[0]):
            continue
        visited[current_city] = element[0]

        if(current_city == end):
            route_taken_format = []
            for x in route_taken_till_now:
                route_taken_format.append((x[0], x[1]['highway'] + " for "+ str(int(x[1]["distance"])) + " miles"))


            return {
                "total-segments" : len(route_taken_format), 
                "total-miles" : route_taken_till_now[-1][-3], 
                "total-hours" : route_taken_till_now[-1][-2], 
                "total-delivery-hours" : route_taken_till_now[-1][-1], 
                "route-taken" : route_taken_format
            }

        # I am storing the total distance, time & delivery hours from start to current city in th route_taken_till_now tuple itself.
        # So, calculating them here itself
        for each_neighbouring_city in successors(G,current_city):
            edge_data = G[current_city][each_neighbouring_city]
            total_segments_till_now = len(route_taken_till_now)
            total_distance_till_now = 0
            total_time_till_now = 0
            total_delivery_hours_till_now = 0
            if(total_segments_till_now):
                total_distance_till_now = route_taken_till_now[-1][2]
                total_time_till_now = route_taken_till_now[-1][3]
                total_delivery_hours_till_now = route_taken_till_now[-1][4]
            
            total_distance_including_current_edge = total_distance_till_now + edge_data["distance"]
            total_time_including_current_edge = total_time_till_now + edge_data["time"]
            
            # Checking the speed limit to determine whether the package will fall or not
            package_fall_prob = 0
            if(edge_data["limit"] >= 50):
                package_fall_prob = tanh(edge_data["distance"]/1000)

            delivery_hours_for_current_edge = edge_data["time"] + package_fall_prob * 2 * (total_delivery_hours_till_now + edge_data["time"])
            total_delivery_hours_including_current_edge = total_delivery_hours_till_now + delivery_hours_for_current_edge

            if(cost.lower() == "distance"):
                fringe.put((f(each_neighbouring_city, end, route_taken_till_now, G, cost), (each_neighbouring_city, route_taken_till_now + [((each_neighbouring_city, edge_data, total_distance_including_current_edge, total_time_including_current_edge, total_delivery_hours_including_current_edge)), ])))

            elif(cost.lower() == "segments"):
                fringe.put((f(each_neighbouring_city, end, route_taken_till_now, G, cost), (each_neighbouring_city, route_taken_till_now + [((each_neighbouring_city, edge_data, total_distance_including_current_edge, total_time_including_current_edge, total_delivery_hours_including_current_edge)), ])))

            elif(cost.lower() == "time"):
                fringe.put((f(each_neighbouring_city, end, route_taken_till_now, G, cost, max_speed_limit), (each_neighbouring_city, route_taken_till_now + [((each_neighbouring_city, edge_data, total_distance_including_current_edge, total_time_including_current_edge, total_delivery_hours_including_current_edge)), ])))

            elif(cost.lower() == "delivery"):
                fringe.put((f(each_neighbouring_city, end, route_taken_till_now, G, cost, max_speed_limit), (each_neighbouring_city, route_taken_till_now + [((each_neighbouring_city, edge_data, total_distance_including_current_edge, total_time_including_current_edge, total_delivery_hours_including_current_edge)), ])))
    
    # If no solution, return empty array with 0 values
    return {"total-segments" : 0, 
            "total-miles" : 0, 
            "total-hours" : 0, 
            "total-delivery-hours" : 0, 
            "route-taken" : []}


# Please don't modify anything below this line
#
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "delivery"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n          Total segments: %4d" % result["total-segments"])
    print("             Total miles: %8.3f" % result["total-miles"])
    print("             Total hours: %8.3f" % result["total-hours"])
    print("Total hours for delivery: %8.3f" % result["total-delivery-hours"])


