##!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Josafat Piraquive

## interference graph classes
#############################
class Graph( object ):
    def __init__( self ):
        self.nodes = {}
        self.edges = set([])
        self.constraint_list = None
    def add_node( self, node ):
        if node.get_name() not in self.nodes:
            self.nodes.update( {node.get_name():node} )
    def get_constraint_list( self ):
        return self.constraint_list
    def add_edge( self, edge ):
        self.edges.add( edge )
    def set_constraint_list( self, constraint_list ):
        self.constraint_list = constraint_list
    def get_most_constraint_node( self ):
        highest_node_cnt = -1
        most_constraint_node = None
        for node_name in self.constraint_list:
            if highest_node_cnt < self.constraint_list[node_name]:
                highest_node_cnt = self.constraint_list[node_name]
                most_constraint_node = node_name
        if most_constraint_node == None:
            return None
        del self.constraint_list[most_constraint_node]
        return self.nodes[most_constraint_node]
    def get_connected_nodes( self, compair_node ):
        connected_nodes = []
        for edge in self.edges:
            if compair_node in edge.get_content():
                for node in edge.get_content():
                    if node != compair_node:
                        connected_nodes.append(node)
        return connected_nodes
    def __str__( self ):
        ident = "    "
        dot = "graph ig {\n"
        for node_name in self.nodes:
            ## print nodes that are not connected
            print_node = True
            for edge in self.edges:
                if self.nodes[node_name] in edge.get_content():
                    print_node = False
            if print_node:
                dot += ident + str(self.nodes[node_name])
            ## print node attributes
            node_attr = self.nodes[node_name].get_dot_attr()
            if node_attr is not "":
                dot += ident + self.nodes[node_name].get_dot_attr()
        ## print edges
        for edge in self.edges:
            dot += ident + str(edge)
        dot+= "}"
        return dot

class Node( object ):
    def __init__( self, content, color=None, v_reg=True ):
        self.content = content
        self.color = color
        self.active = True
        self.v_reg = v_reg
    def get_content( self ):
        return self.content
    def get_color( self ):
        return self.color
    def get_name( self ):
        node_name = self.content.get_name()
        return node_name.replace( '$', '' )
    def set_color( self, new_color ):
        self.color = new_color
        if self.v_reg:
            self.content.set_color( new_color )
    def set_active( self, active ):
        self.active = active
    def is_active( self ):
        return self.active
    def get_dot_attr( self ):
        ret = ""
        if (self.color is not None) and self.v_reg:
            ret = self.get_name() + " [label=\"" + self.get_name() + " [" + self.color.get_name()\
                + "]\", color=\"" + self.color.get_color() + "\"];\n"
        elif (self.color is not None) and not self.v_reg:
            ret = self.get_name() + " [color=\"" + self.color.get_color() + "\"];\n"
        return ret
    def __str__( self ):
        return self.get_name() + ";\n"

class Edge( object ):
    def __init__( self, content ):
        self.content = content
    def get_content( self ):
        return self.content
    def __str__( self ):
        edge_str = ""
        for node in self.content:
            edge_str += "- " + node.get_name() + " -"
        edge_str = edge_str.strip("- ")
        edge_str += ";\n"
        return edge_str 


