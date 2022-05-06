# -*- coding: utf-8 -*-
"""
Created on Wed Apr  6 22:05:50 2022

@author: dngrn
"""

import numpy as np
import matplotlib.pyplot as plt
import fortune.dcel.predicates as pre

class DCEL:
    #%% Initialize
    def __init__(self):
        #Nodes have attributes: coordinates, in-edges, out-edges
        nodes = {}
        #Edges have attributes: source node, twin, prev, next, path list, right-face
        edges = {}
        #Faces have 2 attributes: representative edge, inner components
        faces = {'f0': [[],[]]}

        self.nodes = nodes
        self.edges = edges
        self.faces = faces

    #%% Plot
    def plot(self, plot_nodes=True, plot_edges=True, plot_faces=True):
        offset = 0.1

        #Plot Nodes
        if plot_nodes:
            for node, name in zip(self.nodes.values(), self.nodes.keys()):
                plt.text(node[0][0] + offset, node[0][1] + offset, name)

        #Plot Edges
        for edge, name in zip(self.edges.values(), self.edges.keys()):
            px, py = edge[4][0]
            qx, qy = edge[4][1]

            u = np.array([qx - px, qy - py])
            tx, ty = pre.rotate(u, 0.05)/2
            tx += px
            ty += py

            plt.plot([px, qx], [py, qy], 'bo', linestyle='-')
            if plot_edges:
                plt.text(tx, ty, name, color='red', alpha = 0.5)

        #Plot Faces
        if plot_faces:
            if len(self.edges) > 0: #Length of faces always > 0, but sometime pointer is empty
                for face, name in zip(self.faces.values(), self.faces.keys()):
                    pointer = face[0]
                    edge = self.edges[pointer]
        
                    px, py = edge[4][0]
                    qx, qy = edge[4][1]
        
                    u = np.array([qx - px, qy - py])
                    tx, ty = pre.rotate(u, 0.15)/2
                    tx += px
                    ty += py
        
                    plt.text(tx, ty, name, color='green')


    #%% Add Point
    def add_point(self, point):
        length = len(self.nodes)
        self.nodes[str(length)] = [point, [], []]
        return str(length) #Return the name of the node
    
    def insert_point(self, edge, point):
        """
        Insert new point, n, on existing edge, pq

        Parameters
        ----------
        edge : Namde of edge
        point : List [x,y]

        Returns
        -------
        Name of a new edge created

        """

        
        #%% Name Local Variables
        edge_face = self.edges[edge][-1]
        edge_twin = self.edges[edge][1]
        edge_prev = self.edges[edge][2]
        edge_nex = self.edges[edge][3]
        edge_twin_face = self.edges[edge_twin][-1]
        edge_twin_prev = self.edges[edge_twin][2]
        edge_twin_nex = self.edges[edge_twin][3]
        
        p = self.edges[edge][0]
        length = len(self.nodes)
        n = str(length)
        q = self.edges[edge_twin][0]
        
        p_coord = self.nodes[p][0]
        q_coord = self.nodes[q][0]
        
        new = p + '-' + n
        nex = n + '-' + q
        twin = n + '-' + p
        twin_prev = q + '-' + n
        
        #%% Create New Node
        self.nodes[n] = [point, [new, twin_prev], [nex, twin]]
        
        #%% Update Next and Previous Edges so that Next(Prev(e)) = e
        self.edges[edge_prev][3] = new #Update the next edge of the previous
        self.edges[edge_nex][2] = nex #Update the previous edge of the next
        self.edges[edge_twin_prev][3] = twin_prev #Update the next edge of the twin's previous
        self.edges[edge_twin_nex][2] = twin #Update the previous edge of the twin's next
    
        #%% Treat Annoying Edge Cases where edges point to old split edges
        if edge_nex == edge_twin:
            edge_nex = twin_prev
        if edge_prev == edge_twin:
            edge_prev = twin
        if edge_twin_nex == edge:
            edge_twin_nex = new
        if edge_twin_prev == edge:
            edge_twin_prev = nex
        
        #%% Create new edges
        self.edges[new] = [p, twin, edge_prev, nex, 
                           np.array([p_coord, point]), edge_face]
        self.edges[nex] = [n, twin_prev, new, edge_nex, 
                           np.array([point, q_coord]), edge_face]
        self.edges[twin] = [n, new, twin_prev, edge_twin_nex, 
                            np.array([point, p_coord]), edge_twin_face]
        self.edges[twin_prev] = [q, nex, edge_twin_prev, twin, 
                           np.array([q_coord, point]), edge_twin_face]

        
        #%% Delete Split Edge
        del self.edges[edge]
        del self.edges[edge_twin]
        
        #%% Update Faces
        self.faces[edge_face][0] = new
        self.faces[edge_twin_face][0] = twin
        
        #%% Update Nodes
        self.nodes[p][1].remove(edge_twin) #Remove twin  from in 
        self.nodes[p][2].remove(edge) #Remove edge from out
        self.nodes[q][1].remove(edge) #Remove twin from in 
        self.nodes[q][2].remove(edge_twin) #Remove edge from out
        
        self.nodes[p][1].append(twin) #Add twin to in of p
        self.nodes[p][2].append(new) #Add new to out of p
        self.nodes[q][1].append(nex) #Add nex to in of q
        self.nodes[q][2].append(twin_prev) #Add twin_prev to out of q
        
        return new, n
  
    #%% Get Close edges
    def find_close_edges(self, new, p, q):

        # Get coordinates of points
        p_coord= self.nodes[p][0]
        q_coord = self.nodes[q][0]
        u = np.array(q_coord) - np.array(p_coord)

        min_angle = 5
        max_angle = -1


        ins = self.nodes[p][1] #In edges
        left = self.edges[new][1] #Worst Case Use Twin
        right = self.edges[new][1] #Worst Case Use Twin

        for neighbor in ins:
            v_name = self.edges[neighbor][0] #Source Node Name
            v_coord = self.nodes[v_name][0] #Source Node Coordinate
            v = np.array(v_coord) - np.array(p_coord)
            angle = pre.angle(u, v)
            #print("v name: ",
            #      v_name, "| u: ", u, "| v: ", v, "\nangle: ", angle)
            if angle < min_angle and angle != 0:
                left = neighbor
                min_angle = angle
            if angle > max_angle and angle != 4:
                right = neighbor
                max_angle = angle

        right = self.edges[right][1] #Take Twin
        return left, right

    #%% Add Edge
    def add_edge(self, p, q):
        #Get edge and edge twin names
        new = p + '-' + q
        twin = q + '-' + p
        #print("New: ", new)
        
        if new in self.edges.keys():
            return

        #Update Nodes
        self.nodes[p][1].append(twin)
        self.nodes[p][2].append(new)
        self.nodes[q][1].append(new)
        self.nodes[q][2].append(twin)

        # Get coordinates of points
        p_coord= self.nodes[p][0]
        q_coord = self.nodes[q][0]
        u = np.array(q_coord) - np.array(p_coord)

        #Create new edges
        self.edges[new] = [p, twin, twin, twin, np.array([p_coord, q_coord]),'']
        self.edges[twin] = [q, new, new, new, np.array([q_coord, p_coord]),'']

        #%% Find Previous and Next Edge for New
        prev, nex_twin = self.find_close_edges(new, p, q)
        #print("Prev(", new, ") = ", prev)
        #print("Next(", twin, ") = ", nex_twin)

        #%% Find Previous and Next Edge for Twin
        prev_twin, nex = self.find_close_edges(twin, q, p)
        #print("Next(", new, ") = ", nex)
        #print("Prev(", twin, ") = ", prev_twin)

        #%% Update new edges
        self.edges[new] = [p, twin, prev, nex, np.array([p_coord, q_coord]),'']
        self.edges[twin] = [q, new, prev_twin, nex_twin, np.array([q_coord, p_coord]),'']

        #%% Update Next and Previous Edges so that Next(Prev(e)) = e
        self.edges[prev][3] = new #Update the next edge of the previous
        self.edges[nex][2] = new #Update the previous edge of the next
        self.edges[prev_twin][3] = twin #Update the next edge of the twin's previous
        self.edges[nex_twin][2] = twin #Update the previous edge of the twin's next


        #%% Update Faces By Cycling around until we repeat
        one_face = False
        cycle = nex
        
        while cycle != new:
            if cycle != new and cycle != twin: #Check for already assigned face
                face1 = self.edges[cycle][-1]
            if cycle == twin: #Check if new face is NOT made by new edge
                one_face = True
                if new == self.edges[cycle][3] and len(self.faces) != 1: #Check for lone line
                    face1 = 'f' + str(len(self.faces))
                    self.faces[face1] = [[],[]]
            cycle = self.edges[cycle][3] #Get next edge in the cycle


        if len(self.faces) == 1:
            face1 = 'f0'
            
        self.edges[new][-1] = face1
        self.faces[face1][0] = new #Update Pointer For New Face
    
        if one_face:
            self.edges[twin][-1] = face1
        else:
            face2 = "f" + str(len(self.faces))
            self.edges[twin][-1]= face2
            self.faces[face2] = [twin, []]
            cycle = nex_twin
            while cycle != twin:
                self.edges[cycle][-1] = face2
                cycle = self.edges[cycle][3] #Get next edge in the cycle
        
    def update_faces(self):
        """
        Update Faces for the DCEL.
        Creates cue of all edges, and assigns faces
        sequentially until all edges are removed from cue

        """
        edge_cue = list(self.edges.keys())
        
        #Initialize Face Count
        face_num = 0
        
        while len(edge_cue) > 0:
            
            face_name = 'f' + str(face_num)
            current_edge = edge_cue[0]
            
            cycle = self.edges[current_edge][3]
            self.edges[current_edge][-1] = face_name
            self.faces[face_name] = [current_edge, []]
            del edge_cue[0]
            
            while cycle != current_edge:
                self.edges[cycle][-1] = face_name
                if cycle in edge_cue:
                    edge_cue.remove(cycle)
                cycle = self.edges[cycle][3]
                
            face_num += 1

    def get_node_name(self, point):
        """
        ID the node name from coordinates

        Parameters
        ----------
        point : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        out = '-'
        for node, name in zip(self.nodes.values(), self.nodes.keys()):
                    if node[0] == point:
                        out = name
        return out
                    
if __name__ == "__main__":

    dcel = DCEL()
    
    dcel.add_point([4,5])
    
    dcel.add_point([9,7])

    dcel.add_point([-3,5])   

    dcel.add_edge("0", "1")    

    dcel.add_edge("0", "2")




    dcel.insert_point('1-0', [6,6])
    dcel.add_point([0,6])
    dcel.add_edge("3", "2")
    dcel.add_point([0,7])
    dcel.add_edge("3", "4")
    dcel.add_edge("4", "1")
    dcel.insert_point('2-3', [0,5.5])
    dcel.insert_point('4-1', [4,6.5])
    dcel.add_edge('4', '6')
    dcel.add_point([-2,7])
    dcel.add_edge('4', '8')
    dcel.add_edge('7', '3')

    dcel.update_faces()
    dcel.plot()




