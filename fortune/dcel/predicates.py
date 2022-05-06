# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 21:16:04 2022

@author: dngrn
"""
import numpy as np

def sin(u,v):
    u = np.array(u)
    v = np.array(v)
    if np.dot(u,u) == 0 or np.dot(v,v) == 0: #Check if one of the vectors is 0 vector
        return 0
    return np.dot(u,v) / np.sqrt(np.dot(u,u)*np.dot(v,v))

def cos(u,v):
    u = np.array(u)
    v = np.array(v)
    if np.dot(u,u) == 0 or np.dot(v,v) == 0: #Check if one of the vectors is 0 vector
        return 0
    return np.cross(u,v) / np.sqrt(np.dot(u,u)*np.dot(v,v))

def angle(u,v):
    """
    Returns psuedo-angle between u and v. As v rotates counterclockwise around
    shared origin, angle between u and v goes from 0 to 4.

    Parameters
    ----------
    u : First vector (2 item list)
    v : Second Vector (2 item list)

    Returns
    -------
    angle: floating number between 0 and 4

    """
    s = sin(u,v)
    c = cos(u,v)
    if s == 0 and c == 0:
        return 4
    if s >= 0 and c > 0:
        return c
    elif s <= 0 and c >= 0:
        return -s + 1
    elif s <= 0 and c <= 0:
        return -c + 2
    else:
        return s + 3
    
def rotate(u, theta):
    R = np.array([[np.cos(theta), -np.sin(theta)], 
                  [np.sin(theta), np.cos(theta)]])
    return np.matmul(R, np.array(u))

if __name__ == "__main__":
    u = [0,1]
    v = [-1,1]
    s = sin(u,v)
    c = cos(u,v)
    ang = angle(u,v)
    print("u: ", u, " v: ", v)
    print("Sin angle: ", s)
    print("Cos angle: ", c)
    print("angle: ", ang)
    print("Rotated u", rotate(u, np.pi/2))