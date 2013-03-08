from geopy.distance import distance
from geopy import Point
from itertools import tee, izip

def pairwise(iterable):
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def multi_distance(points):
    total = 0.0
    for a, b in pairwise(points):
        pointA = Point(*reversed(a.location.coords)) 
        pointB = Point(*reversed(b.location.coords)) 
        total += distance(pointA, pointB).m
    return total
