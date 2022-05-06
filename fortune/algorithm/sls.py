# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 09:38:43 2022

@author: dngrn
"""
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 23:31:25 2022

@author: dngrn
"""

import fortune.algorithm.predicates as pred
import fortune.dcel.dcel as struct
import numpy as np

class SLS:
    #%% Initialize
    def __init__(self, points):
        points_sorted = sorted(points, key = lambda x: -x[1])

        #Cue is event - point coordinate - triple
        cue = [['site', point, []] 
                for i, point in enumerate(points_sorted)]
        
        y_list = [y for x,y in points_sorted]
        
        del cue[0]
        del y_list[0]
        self.cue = cue
        self.y_list = y_list
        
        self.arcs = {'arc-1' : [points_sorted[0],'empty', 'empty']}
        self.beach_root = 'arc-1'
        self.arc_number = 2
        
        
        self.graph = []
        self.dcel = struct.DCEL()
        
        
        
        
        a = self.dcel.add_point([15,15])
        b = self.dcel.add_point([0,15])
        c = self.dcel.add_point([15,0])
        d = self.dcel.add_point([0,0])
        
        self.dcel.add_edge(a, b)
        self.dcel.add_edge(b, d)
        self.dcel.add_edge(d, c)
        self.dcel.add_edge(c, a)

        self.boundary = b + '-' + a

                
    #%%Locate new site on Beach Line
    def locate_new(self, new):
        """
        Find the corresponding arc that a vertical line extending
        from the new site passes through. This is done with a 
        binary search
    
        Parameters
        ----------
        beach_line : list of points that correspond to the left to 
        right arcs of the beach line
        new : [x,y] point location of the new site
    
        Returns
        -------
        index of arc that the new site vertical line passes through
    
        """
        #Identify x-value of new site
        x = new[0]
        h = new[1]
    
        
        #Initialize Index
        n = len(self.arcs)
                
        #Initialize Solution
        search = True
        arc = self.beach_root
        p = self.arcs[arc][0]
        
        #If beachline has one element
        if n == 1:
            return arc
        
        #Search successive arcs until test exceeds input x value
        while search:
            next_arc = self.arcs[arc][2]  
            
            if next_arc == 'empty':
                return arc
            else:
                q = self.arcs[next_arc][0]

            
            #Degeneracy test
            if p[1] != h and q[1] != h:
                x_test = pred.get_breakpoint(h, p, q)
                if x_test > x:
                    search = True
                    return arc 
            else:
                next_arc = self.arcs[arc][2]
                arc = next_arc
                

            
            #Increment
            arc = next_arc
            p = q
            
        
    #%% Insert new arc
    def insert_arc(self, location, new):
        """
        Splits location arc and inserts a new arc at location new

        Parameters
        ----------
        location : string name of location arc
        new : [x,y] coordinate of new arc point

        """
        #Delete arc
        coord, left, right =  self.arcs.pop(location)
        
        #Name new arc to beach line
        new_left = 'arc-' + str(self.arc_number)
        self.arc_number += 1
        
        #Name arc left to beach line
        new_name = 'arc-' + str(self.arc_number)
        self.arc_number += 1
        
        #Name arc right to beach line
        new_right = 'arc-' + str(self.arc_number)
        self.arc_number += 1
        
        #Create left arc
        self.arcs[new_left] = [coord, left, new_name]
        
        #Create new splitting arc
        self.arcs[new_name] = [new, new_left, new_right]
        
        #Create new right splitting arc
        self.arcs[new_right] = [coord, new_name, right]
        
        #Update left and right arcs
        if left != 'empty':
            self.arcs[left][2] = new_left
        if right != 'empty':
            self.arcs[right][1] = new_right
            
        #Update Beach Line Root
        if self.beach_root == location:
            self.beach_root = new_left
            
        #Return new name
        return new_name
    
    #%% ADD VERTEX EVENT
    def add_vertex_event(self, left, middle, right, y):
        """
        Add vertex event to cue if it doesn't already exist.
        Not added if points collinear
        Not added if circle isn't below middle point

        Parameters
        ----------
        left : left arc
        middle : middle arc
        right : right arc
        y: y-value of sweep line

        """
        #Get coordinates defining circle
        v1 = self.arcs[left][0]
        v2 = self.arcs[middle][0]
        v3 = self.arcs[right][0]
        if pred.area2(v1, v2, v3) < 0: #Check if points are collinear
            center, h = pred.findCircle(v1, v2, v3)
        
            #Check if circle is below current y-coordinate of sweep
            if h <= y:
                
                #Check if vertex is already in the cue
                for event in self.cue:
                    
                    if event[0] == 'vertex': #Make sure event is a vertex
                        
                        if (left in event[2] and #Check if all arcs are in the redundant vertex
                            middle in event[2] and
                            right in event[2]):
                            
                            return
                
                #If new vertex is indeed unique, add to correct location in queue            
                index = pred.bisect(self.y_list, h) #Find index in log(n) time
                
                self.cue.insert(index, ['vertex', center, [left, middle, right], h])
                self.y_list.insert(index, h)
        
    #%% DELETE VERTEX    
    def delete_vertex_event(self, old_arc):
        """
        Remove all vertex events from the cue that have a specified arc

        Parameters
        ----------
        old_arc : arc that was either split or disappeared

        """
        #Loop over all events
        n = len(self.cue)
        for i, event in enumerate(reversed(self.cue)):
            
            if event[0] == 'vertex': #Only check vertex events
                
                if old_arc in event[2]:
                    
                    del self.cue[n - i - 1]
                    del self.y_list[n - i - 1]

    
    #%% FIND SPLIT VERTICES
    def find_split_vertices(self, new):
        """
        Add up to four vertex events in cue after splitting and inserting
        new site event.
        left vertex is added if two arcs exist left of new arc and if 
        coordinates are not collinear and circle goes below y value of new coord.
        right vertex is added similarly

        Parameters
        ----------
        new : arc name of newly inserted arc from site event

        """
        #Get Left and Right Arcs of the newly inserted arc
        left = self.arcs[new][1]
        right = self.arcs[new][2]
        
        #Get y-value of sweep line
        y = self.arcs[new][0][1]
        
        #Consider vertex that could be made to the left
        if left != 'empty':
            
            left_left = self.arcs[left][1] #left 2 of new arc
            
            #Make sure vertex is defined by 3 points
            if left_left != 'empty': 
                
                self.add_vertex_event(left_left, left, new, y)
                
                #leftmost possible vertex event
                left_left_left = self.arcs[left_left][1]
                                                               
                if left_left_left != 'empty':
                    
                    self.add_vertex_event(left_left_left, left, left, y)

        
        #Consider Vertex that could be made to the right
        if right != 'empty':
            
            right_right = self.arcs[right][2] #right 2 of the new arc
            
            #Make sure vertex is defined by 3 points
            if right_right != 'empty': 
            
                self.add_vertex_event(new, right, right_right, y)
                
                #Get right_right centered vertex
                right_right_right = self.arcs[right_right][2]
                                                               
                if right_right_right != 'empty':
                    
                    self.add_vertex_event(right, right_right, right_right_right, y)

         
    #%% DELETE A SHRINKED ARC FROM VERTEX EVENT
    def delete_arc(self, old_arc):
        """
        When an arc is shrunk to 0 at vertex event, the beach line must
        be updated. The old arc is removed, and its neighbors are updated

        Parameters
        ----------
        old_arc : name of arc being removed

        """
        
        coord, left, right = self.arcs.pop(old_arc)
        
        #Update left and right arcs
        if left != 'empty':
            self.arcs[left][2] = right
        if right != 'empty':
            self.arcs[right][1] = left
            
        #Update Beach Line Root
        if self.beach_root == old_arc:
            self.beach_root = right


    #%% CREATE NEW VERTEX EVENTS FROM VERTEX EVENT
    def find_vertex_vertices(self, left, middle, right, y):
        """
        Find possible two vertices that can arise from vertex event.
        1) left_left, left, right
        2) left, right, right_right

        Parameters
        ----------
        left : left arc from vertex
        middle : middle arc from vertex
        right : right arc from vertex
        y : hieght of bottom of circle

        """
        #Get neighboring arcs
        left_left = self.arcs[left][1] 
        right_right = self.arcs[right][2] 
        
        #Add vertex from new left triple
        if left_left != 'empty' and left_left != right:
            
            self.add_vertex_event(left_left, left, right, y)
            
        #Add vertex from new left triple
        if right_right != 'empty' and left != right_right:
            
            self.add_vertex_event(left, right, right_right, y)
            
        

    #%% NEXT EVENT
    def next_event(self):
        """
        Returns next event in cue and simultaneously 
        deletes it from the cue

        Returns
        -------
        event : The first event in the cue

        """
        event = self.cue[0]
        
        del self.cue[0] #Remove event from cue
        del self.y_list[0] #Remove y value from y list
        
        return event


    #%% GRAPH                         
    def create_dangle(self, a, b, connections = 0):
        
        p, q = pred.sort(a,b)
        #Create graph object. p & q form line, with bisector.
        #Next entry is the end points (names of nodes in dcel)
        #Next +1/-1 if anchor is left of its roots
        #Next Entry is first anchor
        #Last entry is the number of connections
        self.graph.append([p, q, 1, [], 0])
    
    #%% FIND A DANGLE BETWEEN POINTS
    def find_dangle(self, p, q):
        a, b = pred.sort(p, q)
        i = 0
        while i < len(self.graph):
            end = self.graph[i]
            c = end[0]
            d = end[1]
            if a == c and b == d:
                return i #Return dangle index and dangle node name
            else:
                i += 1
        return -1
    
    #%% GRAPH VERTEX
    def graph_vertex(self, vertex, left, middle, right):
        
        l = self.arcs[left][0]
        p = self.arcs[middle][0]
        q = self.arcs[right][0]
        
        b1 = pred.get_bisector(l, p)
        b2 = pred.get_bisector(p, q)
        b3 = pred.get_bisector(q, l)
        
        #Find if vertex is in triangle l,p,q
        in_triangle = pred.point_in_tri(vertex, [l, p, q])
        
                    

        #Create Node
        name = self.dcel.add_point(vertex)

        #Find lp dangle (if it exists)
        i = self.find_dangle(l, p)
        if i != -1: #Add vertex to existing dangle
        
            if not in_triangle and pred.point_in_tri(b1, [b2,b3,vertex]):
                self.graph[i][2] = False
            else:
                self.graph[i][2] = True
            
            self.graph[i][3].append(name)
            self.graph[i][4] += 1
            
            if self.graph[i][4] == 2: #If dangle is complete
                node1, node2 = self.graph[i][3]
                self.dcel.add_edge(node1, node2)
                del self.graph[i]        
        
            
        #Find pq dangle (if it exists)
        i = self.find_dangle(p, q)
        if i != -1: #Add vertex to existing dangle
            if not in_triangle and pred.point_in_tri(b2, [b1,b3,vertex]):
                self.graph[i][2] = False
            else:
                self.graph[i][2] = True
            self.graph[i][3].append(name)
            self.graph[i][4] += 1

            
            if self.graph[i][4] == 2: #If dangle is complete
                node1, node2 = self.graph[i][3]
                self.dcel.add_edge(node1, node2)
                del self.graph[i]
        
        
        #Create new dangle from vertex
        #pred.point_in_poly(vertex, [l,p,q])
        a, b = pred.sort(l,q)
        
        convex_angle = pred.angle_between(b1, vertex, b3) > np.pi/2

        self.graph.append([a, b, convex_angle, [name], 1])

    #%% EXTEND DANGLES    
    def extend_dangles(self):
        #Loop over all dangles
        for end in self.graph:
            
            if end[4] == 0:
                print("floating bisector", end)
            
            else:
                a, b = end[0], end[1]
                bisector = pred.get_bisector(a, b)
                node = end[3][0]
                vert = self.dcel.nodes[node][0]
                vert_to_bisect = end[2]
                if vert_to_bisect:
                    direction_vector = [(bisector[0] - vert[0]), (bisector[1] - vert[1])]
                else:
                    direction_vector = [(vert[0] - bisector[0]), (vert[1] - bisector[1])]

                
                max_component = min(abs(direction_vector[0]),abs(direction_vector[1]))
                scale = 200 / (max_component + 0.001)
                #scale = 200
                outside = [vert[0] + scale * direction_vector[0], vert[1] + scale * direction_vector[1]]
                
                boundary_seed = self.boundary
                
                cycle = boundary_seed
                next_cycle = self.dcel.edges[cycle][3]
                
                found = False
                
                while next_cycle != boundary_seed and not found:
                    
                    node1 = self.dcel.edges[cycle][0]
                    node2 = self.dcel.edges[next_cycle][0]
                    coord1 = self.dcel.nodes[node1][0]
                    coord2 = self.dcel.nodes[node2][0]

                    
                    if pred.intersectProp(coord1, coord2, vert, outside):
                        intersect = pred.intersection(coord1, coord2, vert, outside)
                        self.boundary, new_node = self.dcel.insert_point(cycle, intersect)
                        self.dcel.add_edge(node, new_node)
                        found = True
                        
                    cycle = next_cycle
                    next_cycle = self.dcel.edges[cycle][3]
                    

        
if __name__ == "__main__":
    
    points = [[0,0],[1,1],[2,2],[3,3],[3,2],[3,0],[2,0],[1,0]]
    sls = SLS(points) 
    #print("CUE: ", sls.cue)    
    #print("ARCS: ", sls.arcs)
    
    #TEST INSERT
    coord = [1,1]
    location = sls.locate_new(coord)
    sls.delete_vertex_event(location)
    new = sls.insert_arc(location, coord)
    sls.find_split_vertices(new)
    print("Location: ", location)
    print("Arcs: ", sls.arcs)
    
    coord = [3,0]
    location = sls.locate_new(coord)
    sls.delete_vertex_event(location)
    new = sls.insert_arc(location, coord)
    sls.find_split_vertices(new)
    print("Location: ", location)
    print("Arcs: ", sls.arcs)
    
    coord = [-1,-1]
    location = sls.locate_new(coord)
    sls.delete_vertex_event(location)
    new = sls.insert_arc(location, coord)
    sls.find_split_vertices(new)
    print("Location: ", location)
    print("Arcs: ", sls.arcs)
    
    coord = [-1,-2]
    location = sls.locate_new(coord)
    sls.delete_vertex_event(location)
    new = sls.insert_arc(location, coord)
    sls.find_split_vertices(new)
    print("Location: ", location)
    print("Arcs: ", sls.arcs)
    
    #Delete Arcs
    #sls.delete_arc('arc-13')
    #sls.delete_arc('arc-2')
    print("Arcs: ", sls.arcs)
    
    #Find vertex events
    sls.find_vertex_vertices('arc-12', 'arc-10', 'arc-13', 10)
    #sls.delete_vertex_event('arc-10')
    #sls.delete_arc('arc-10')
  
