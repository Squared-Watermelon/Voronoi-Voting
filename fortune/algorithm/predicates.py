# -*- coding: utf-8 -*-
"""
Created on Mon Apr 18 00:39:35 2022

@author: dngrn
"""
import numpy as np
import bisect
import math

def angle_between(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3

    v21 = (x1 - x2, y1 - y2)
    v23 = (x3 - x2, y3 - y2)

    dot = v21[0] * v23[0] + v21[1] * v23[1]
    det = v21[0] * v23[1] - v21[1] * v23[0]

    theta = np.rad2deg(np.arctan2(det, dot))

    return theta

def point_in_tri(coord, polygon):

    a, b, c = polygon #Unpack polygon
    
    l1 = left(a, b, coord)
    l2 = left(b, c, coord)
    l3 = left(c, a, coord)
    
    left_in = (l1 and l2 and l3)
    right_in = (not l1 and not l2 and not l3)
    
    return  left_in or right_in 
    
    

def get_breakpoint(h, p, q):
    """
    Find the x-value of the point equidistant from
    line y=h, and points p and q.

    Parameters
    ----------
    h : y-value of sweep line
    p : [x,y] point corresponding to left arc
    q : [x,y] point corresponding to right arc

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    #Break Points into components
    a, b = p 
    c, d = q
    
    root = np.sqrt(((a-c)**2 + (b-d)**2)/((b-h)*(d-h)))
    
    if b == d: #Avoid divide by zero error when two points have same y value
        return (a + c) / 2
    else:
        return (a * (h - d) + (b - h) * (c + root * (h - d))) / (b - d)
    

def area2(a, b, c):
     
    """ Calculation the 2 * area of 
        triangle """
        
    area = ((b[0] - a[0]) * (c[1] - a[1]) -
         (c[0] - a[0]) * (b[1] - a[1]))
 
    return area

def collinear(a, b, c):
    return area2(a, b, c) == 0

def left(a, b, c):
    return area2(a, b, c) > 0

def xor(t1, t2):
    if t1 and not t2:
        return True
    elif not t1 and t2:
        return True
    else:
        return False

def intersectProp(a, b, c, d):
    '''
    Boolean value for whether two line segments intersect

    Parameters
    ----------
    a : first point of first line segment
    b : second point of first line segment
    c : first point of second line segment
    d : second point of second line segment

    '''
    #Eliminate Improper Cases
    if (
        collinear(a,b,c) or
        collinear(a,b,d) or
        collinear(c,d,a) or
        collinear(c,d,b)):
        return False
    
    return (xor(left(a,b,c), left(a,b,d)) and
            xor(left(c,d,a), left(c,d,b)))

def intersection(a, b, c, d):
    
    v1 = [a[0], a[1], 1]
    v2 = [b[0], b[1], 1]
    v3 = [c[0], c[1], 1]
    v4 = [d[0], d[1], 1]
    
    x, y, z = np.cross(np.cross(v1, v2), np.cross(v3, v4))
    
    return [x/z, y/z]
    
    
    
    
        
# Function to find the circle on
# which the given three points lie
def findCircle(v1, v2, v3):
    x1, y1 = v1
    x2, y2 = v2
    x3, y3 = v3
    
    x12 = x1 - x2
    x13 = x1 - x3
    
    y12 = y1 - y2
    y13 = y1 - y3
    
    y31 = y3 - y1
    y21 = y2 - y1
    
    x31 = x3 - x1
    x21 = x2 - x1
    
    # x1^2 - x3^2
    sx13 = pow(x1, 2) - pow(x3, 2)
    
    # y1^2 - y3^2
    sy13 = pow(y1, 2) - pow(y3, 2)
    
    sx21 = pow(x2, 2) - pow(x1, 2)
    sy21 = pow(y2, 2) - pow(y1, 2)
    
    f = (((sx13) * (x12) + (sy13) *
    	(x12) + (sx21) * (x13) +
    	(sy21) * (x13)) / (2 *
    	((y31) * (x12) - (y21) * (x13))))
    			
    g = (((sx13) * (y12) + (sy13) * (y12) +
    	(sx21) * (y13) + (sy21) * (y13)) /
    	(2 * ((x31) * (y12) - (x21) * (y13))))
    
    c = (-pow(x1, 2) - pow(y1, 2) -
    	2 * g * x1 - 2 * f * y1)
    
    # eqn of circle be x^2 + y^2 + 2*g*x + 2*f*y + c = 0
    # where centre is (h = -g, k = -f) and
    # radius r as r^2 = h^2 + k^2 - c
    h = -g
    k = -f
    sqr_of_r = h * h + k * k - c
    
    # r is the radius
    r = np.sqrt(sqr_of_r)
        
    #print("Centre = (", h, ", ", k, ")")
    #print("Radius = ", r)
    #print("Intersection Point: ", h, ", ", k - r)
    
    return [h, k], k - r

def find_index(y_list, y):
    return bisect.bisect_left(y_list, y)

def insert_vertex(vertex, y_list):
    v_point = findCircle(vertex)
    index = find_index(y_list, v_point[1])
    return v_point[1], index, ['vertex', v_point, vertex]

def get_bisector(p, q):
    x = (p[0] + q[0]) / 2
    y = (p[1] + q[1]) / 2
    return [x, y]  

def bisect(arr, val):
    cmp = lambda x, y: x > y
    l = -1
    r = len(arr)
    while r - l > 1:
        e = (l + r) >> 1
        if cmp(arr[e], val): l = e
        else: r = e
    return r

def sort(a,b):
    """
    Returns 2 points in order with
    first point higher and further to the right than second
    """
    if a[1] > b[1]:
        p = a
        q = b
    elif a[1] < b[1]:
        p = b
        q = a
    elif a[0] > b[1]:
        p = a
        q = b
    else:
        p = b
        q = a
        
    return p, q

if __name__ == "__main__":
    a = [-1,1]
    b = [1,1]
    c = [0,-2]
    d = [-1,1]
    
    print(intersectProp(a, b, c, d))
    print(intersection(a, b, c, d))
    
    a = [-1, 3]
    b = [8, 1]
    c = [0,0]
    print(findCircle(a,b,c))
    
    print("Point in poly: ", point_in_tri([3.7, 1.5], [a,b,c]))
    
    
        
        
    