import pygame.math
import numpy

'''def rayTheoryCollision(polygon1, polygon2):
    rayMinX = polygon1[0] #Assume a random point that has the lowest x
    rayMaxX = polygon1[0] #Assume a random point that has the greatest x
    rayY = polygon1[0] #Assume a random point that has the lowest y
    poly1MaxY = polygon1[0]
    poly1MinY = polygon1[0]
    poly2MaxY = polygon2[0]
    poly2MinY = polygon2[0]
    
    for point in polygon1:
        #Get ray points
        if point[0] < rayMinX[0]:
            rayMinX = point
        elif point[0] > rayMaxX[0]:
            rayMaxX = point
        if point[1] < rayY[1]:
            rayY = point

        if point[1] < poly1MinY[1]:
            poly1MinY = point
        elif point[1] > poly1MaxY[1]:
            poly1MaxY = point

    for point in polygon2:
        #Get ray points
        if point[0] < rayMinX[0]:
            rayMinX = point
        elif point[0] > rayMaxX[0]:
            rayMaxX = point
        if point[1] < rayY[1]:
            rayY = point

        if point[1] < poly2MinY[1]:
            poly2MinY = point
        elif point[1] > poly2MaxY[1]:
            poly2MaxY = point

    if poly2MaxY[1] > poly1MaxY[1] and poly2MinY[1] < poly1MinY[1]: #Polygon 2 covers polygon 1
        rayDropY = poly2MaxY[1] - poly2MinY[1]
    elif poly1MaxY[1] > poly2MaxY[1] and poly1MinY[1] < poly2MinY[1]: #Polygon 1 covers polygon 2
        rayDropY = poly1MaxY[1] - poly1MinY[1]
    else:
        rayDropY = max(poly1MaxY[1] - poly2MinY[1], poly2MaxY[1] - poly2MinY[1])#Amount to decrease in y
    #rayY = (rayY[0], rayY[1]-rayDropY)
    return rayMinX, rayY, rayMaxX
'''

def getArea(triangle):
    #P = point
    prevP, currP, nextP = triangle
    vector1 = pygame.math.Vector2(prevP[0] - currP[0], prevP[1] - currP[1])
    vector2 = pygame.math.Vector2(nextP[0] - currP[0], nextP[1] - currP[1])
    area = vector1.cross(vector2)/2
    return abs(area)
    
def polygonToTriangles(polygon): #O(2n) time complexity
    backUp = [point for point in polygon]
    firstTriangles = []
    secondTriangles = []
    previousPoint = None
    currentPoint = None
    nextPoint = None
    totalArea = 0
    while len(polygon) > 3:
        length = len(polygon)
        previousPoint = polygon[length-1]
        currentPoint = polygon[0]
        nextPoint = polygon[1]
        triangle = (previousPoint, currentPoint, nextPoint)
        totalArea += getArea(triangle)
        firstTriangles.append(triangle)
        polygon.pop(0)
    firstTriangles.append(polygon)
    totalArea += getArea(polygon)
    totalArea2 = 0
    while len(backUp) > 3:
        length = len(backUp)
        previousPoint = backUp[0]
        currentPoint = backUp[1]
        nextPoint = backUp[2]
        triangle = (previousPoint, currentPoint, nextPoint)
        totalArea2 += getArea(triangle)
        secondTriangles.append(triangle)
        backUp.pop(1)
    secondTriangles.append(backUp)
    totalArea2 += getArea(backUp)
    if totalArea <= totalArea2:
        return firstTriangles
    else:
        return secondTriangles

def polygonCollide(p1, p2):
    #set of v vectors for polygon 1 and 2

    p1 = [numpy.array(vector, 'float64') for vector in p1]
    p2 = [numpy.array(vector, 'float64') for vector in p2]
    
    edges = edges_of(p1) + edges_of(p2)
    orthogonals = [numpy.array([-edge[1], edge[0]]) for edge in edges]

    push_vectors = []
    for o in orthogonals:
        separates, pv = is_separating_axis(o, p1, p2)

        if separates:
            # they do not collide and there is no push vector
            return False, None
        else:
            push_vectors.append(pv)

    # they do collide and the push_vector with the smallest length is the MPV
    mpv =  min(push_vectors, key=(lambda v: numpy.dot(v, v)))

    # assert mpv pushes p1 away from p2
    d = centers_displacement(p1, p2) # direction from p1 to p2
    if numpy.dot(d, mpv) > 0: # if it's the same direction, then invert
        mpv = -mpv

    return True, mpv

def centers_displacement(p1, p2):
    """
    Return the displacement between the geometric center of p1 and p2.
    """
    # geometric center
    c1 = numpy.mean(numpy.array(p1), axis=0)
    c2 = numpy.mean(numpy.array(p2), axis=0)
    return c2 - c1

def edges_of(vertices):
    edges = []
    length = len(vertices)
    for i in range(length):
        edge = vertices[(i+1)%length] - vertices[i]
        edges.append(edge)
    return edges

def is_separating_axis(o, p1, p2):
    """
    Return True and the push vector if o is a separating axis of p1 and p2.
    Otherwise, return False and None.
    """
    min1, max1 = float('+inf'), float('-inf')
    min2, max2 = float('+inf'), float('-inf')

    for v in p1:
        projection = numpy.dot(v, o)

        min1 = min(min1, projection)
        max1 = max(max1, projection)

    for v in p2:
        projection = numpy.dot(v, o)

        min2 = min(min2, projection)
        max2 = max(max2, projection)

    if max1 >= min2 and max2 >= min1:
        d = min(max2 - min1, max1 - min2)
        # push a bit more than needed so the shapes do not overlap in future
        # tests due to float precision
        d_over_o_squared = d/numpy.dot(o, o) + 1e-10
        pv = d_over_o_squared*o
        return False, pv
    else:
        return True, None
