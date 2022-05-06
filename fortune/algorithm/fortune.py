# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 13:41:52 2022

@author: dngrn
"""
import fortune.algorithm.sls as sweep
import fortune.dcel.dcel as struct
import numpy as np
import matplotlib.pyplot as plt


#%% Point Sets
random = (10 * np.random.rand(100,2)+2).tolist()
data = [[12.9631, 6.5124], [13.6467, 7.8596], [12.1197, 8.8195], [10.4191, 
          0.760492], [8.97919, 1.94532], [10.3717, 5.19051], [8.7605, 
          8.96283], [7.13738, 0.819094], [8.49337, 5.96548], [6.57412, 
          8.93226], [6.69842, 11.0437], [4.1932, 3.76347], [4.19631, 
          6.29002], [4.35651, 9.91123], [0.955666, 4.36963], [1.08977, 
          8.5243], [0.284, 5.44423]]
 
                                                              
#%% Pick set of points                                                              
print('------------------------')
print('1: 100 random points \n2: Actual Data')      
                                                        
choice = input("Pick which data to run on: ")
                                           
if choice == '1':
    points = random
else:
    points = data



#%% Initialize sweep line status and graph
sls = sweep.SLS(points)
dcel = struct.DCEL()

#%% Loop until cue is empty
while len(sls.cue) > 0:

    #Get next event in the cue
    next_event = sls.next_event()
    
    #%% Site Event
    if next_event[0] == 'site':
        
        #[x,y] coordinate of site
        coord = next_event[1] 
        
        #arc the new site intersects
        location = sls.locate_new(coord) 
 
        #CREATE DANGLING EDGE OF BISECTOR        
        old_coord = sls.arcs[location][0]
        sls.create_dangle(old_coord, coord)
        
        #Insert new arc and update beach line
        new = sls.insert_arc(location, coord)
        
        #Delete vertex events in cue associated with old arc
        sls.delete_vertex_event(location) 
        
        #Find and add new vertices that arise from split
        left = sls.arcs[new][1]
        right = sls.arcs[new][2]

        sls.find_split_vertices(left)
        sls.find_split_vertices(new)
        sls.find_split_vertices(right)

    #%% Vertex Event  
    if next_event[0] == 'vertex':
        
        #Name Arcs
        vertex = next_event[1]
        left, middle, right = next_event[2]
        y = next_event[3]
        
        #Tie down edges to vertex and create new dangling edge
        sls.graph_vertex(vertex, left, middle, right)
        
        #Delete Middle Arc From Beachline
        sls.delete_arc(middle)
        
        #Delete vertex events associated with vanishing arc
        sls.delete_vertex_event(middle)
        
        #Find and add new vertices that arise from vanished arc
        sls.find_vertex_vertices(left, middle, right, y)

#%% Connect 'dangling' edges to edges of bounding box
sls.extend_dangles()


#%% Plot DCEL and points
plt.figure()
for point in points:
    plt.plot(point[0], point[1], 'r+')  
plt.gca().set_aspect('equal')

sls.dcel.plot(plot_nodes=False, plot_edges=False, plot_faces=False)
plt.xlim([0,15])
plt.ylim([0,15])
