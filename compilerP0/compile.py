#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Josafat Piraquive
# (Lothar Rubusch) contributer for prior steps of the project

"""
USAGE:
$ python ./interp.py ./input.txt

TEST:
$ python ./test_interp.py
"""

import sys
import os.path
import compiler
import copy

## auxiliary
def die( meng ):
    print meng
    sys.exit( -1 )

def usage():
    print "USAGE:"
    print "    %s <inputfile>" % sys.argv[0]
    print "or"
    print "    %s <inputfile> DEBUG" % sys.argv[0]


## ASM descriptor classes
#########################

# label element (i.e main:)
class ASM_label( object ):
    def __init__( self, name ):
        self.DEBUG_type = "ASM_label"
        self.name = name
    def __str__( self ):
        return self.name + ":"

# text description used for the header
class ASM_text( object ):
    def __init__( self, text ):
        self.DEBUG_type = "ASM_text"
        self.text = text
    def __str__( self ):
        return "        ." + self.text


## ASM operand classes
######################

# register of X86 (%eax, %ebx, etc...)
class ASM_register( object ):
    def __init__( self, name, caller=True, color='white' ):
        self.name = name
        self.color = color
        self.caller = caller
    def get_name( self ):
        return self.name
    def get_color( self ):
        return self.color
    def is_caller( self ):
        return self.caller
    def __str__( self ):
        return "%" + self.name

# virtual registers used for pseudo assembly
class ASM_v_register( object ):
    def __init__( self, name, spilled=False ):
        self.name = name
        self.spilled = spilled
        self.new = False
        self.spilled_name = None
    def get_name( self ):
        return self.name
    def is_spilled( self ):
        return self.spilled
    def set_spilled( self, spilled ):
        self.spilled = spilled
    def is_new( self ):
        return self.new
    def set_new( self, new_val ):
        self.new = new_val
    def get_spilled_name( self ):
        return self.spilled_name
    def set_spilled_name( self, name ):
        self.spilled_name = name
    def __str__( self ):
        return self.name

# object indicating the stack position
class ASM_stack( object ):
    def __init__( self, pos, stackptr ):
        self.pos = pos
        self.stackptr = stackptr
    def get_pos( self ):
        return self.pos
    def __str__( self ):
        pos_str = ''
        if self.pos != 0:
            pos_str = str(self.pos)
        return  pos_str + "(" + str(self.stackptr) + ")"

# constant (i.e. $3)
class ASM_immedeate( object ):
    def __init__(self, val ):
        self.val = val
    def get_val( self ):
        return self.val
    def __str__( self ):
        return '$%d' % self.val


# function names and goto labels
class ASM_name( object ):
    def __init__(self, name ):
        self.name = name
    def get_name( self ):
        return self.name
    def __str__( self ):
        return self.name


## ASM Instruction classes
##########################

# parent class of all instructions
class ASM_instruction( object ):
    def __init__( self ):
        self.DEBUG_type = ""
        self.inst_ident = "        "
        self.r_use = []
        self.r_def = []
        self.r_ignore = []
    def get_r_use( self ):
        return self.r_use
    def get_r_def( self ):
        return self.r_def
    def get_r_ignore( self ):
        return self.r_ignore
    def set_r_use( self, var ):
        if isinstance( var, ASM_v_register ) or isinstance( var, ASM_register ):
            self.r_use.append( Live( var ) )
    def set_r_def( self, var ):
        if isinstance( var, ASM_v_register ) or isinstance( var, ASM_register ):
            self.r_def.append( Live( var ) )
    def set_r_ignore( self, var ):
        if isinstance( var, ASM_register ):
            self.r_ignore.append( Live( var, True ) )
    def print_debug( self ):
        return self.DEBUG_type

# move 
class ASM_movl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_movl, self).__init__() 
        self.DEBUG_type = "ASM_movl"
        self.left = left
        self.right = right
        self.set_r_use( left )
        self.set_r_def( right )
    def __str__( self ):
        return self.inst_ident + "movl " + str(self.left) + ", " + str(self.right)

# push
class ASM_pushl( ASM_instruction ):
    def __init__( self, op ):
        super(ASM_pushl, self).__init__() 
        self.DEBUG_type = "ASM_pushl"
        self.op = op
    def __str__( self ):
        return self.inst_ident + "pushl " + str(self.op)

# add 
class ASM_addl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_addl, self).__init__() 
        self.DEBUG_type = "ASM_addl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "addl " + str(self.left) + ", " + str(self.right)

# subtract
class ASM_subl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_subl, self).__init__() 
        self.DEBUG_type = "ASM_subl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "subl " + str(self.left) + ", " + str(self.right)

# unary sub
class ASM_negl( ASM_instruction ):
    def __init__( self, op ):
        super(ASM_negl, self).__init__() 
        self.DEBUG_type = "ASM_negl"
        self.op = op
        self.set_r_def( op )
        self.set_r_use( op )
    def __str__( self ):
        return self.inst_ident + "negl " + str(self.op)

# bitand
class ASM_andl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_andl, self).__init__() 
        self.DEBUG_type = "ASM_andl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "andl " + str(self.left) + ", " + str(self.right)

# bitor
class ASM_orl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_orl, self).__init__() 
        self.DEBUG_type = "ASM_orl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "orl " + str(self.left) + ", " + str(self.right)

# bitxor
class ASM_xorl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_xorl, self).__init__() 
        self.DEBUG_type = "ASM_xorl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "xorl " + str(self.left) + ", " + str(self.right)

# bitinvert
class ASM_notl( ASM_instruction ):
    def __init__( self, op ):
        super(ASM_notl, self).__init__() 
        self.DEBUG_type = "ASM_notl"
        self.op = op
        self.set_r_def( op )
        self.set_r_use( op )
    def __str__( self ):
        return self.inst_ident + "notl " + str(self.op)

# multiplication
class ASM_imull( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_imull, self).__init__() 
        self.DEBUG_type = "ASM_imull"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "imull " + str(self.left) + ", " + str(self.right)

# function call
class ASM_call( ASM_instruction ):
    def __init__( self, name ):
        super(ASM_call, self).__init__() 
        self.DEBUG_type = "ASM_call"
        self.name = name
    def __str__( self ):
        return self.inst_ident + "call " + str(self.name)

# return
class ASM_ret( ASM_instruction ):
    def __init__( self ):
        super(ASM_ret, self).__init__() 
        self.DEBUG_type = "ASM_ret"
    def __str__( self ):
        return self.inst_ident + "ret"

# leave
class ASM_leave( ASM_instruction ):
    def __init__( self ):
        super(ASM_leave, self).__init__() 
        self.DEBUG_type = "ASM_leave"
    def __str__( self ):
        return self.inst_ident + "leave"

# shift left
class ASM_shll( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_shll, self).__init__() 
        self.DEBUG_type = "ASM_shll"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "shll " + str(self.left) + ", " + str(self.right)

# shift right
class ASM_shrl( ASM_instruction ):
    def __init__( self, left, right ):
        super(ASM_shrl, self).__init__() 
        self.DEBUG_type = "ASM_shrl"
        self.left = left
        self.right = right
        self.set_r_def( left )
        self.set_r_use( left )
        self.set_r_use( right )
    def __str__( self ):
        return self.inst_ident + "shrl " + str(self.left) + ", " + str(self.right)

## liveness object
##################
class Live( object ):
    def __init__( self, content, ignore=False ):
        self.content = content
        self.ignore = ignore ## used for special handling of registers (i.e. call)
    def get_content( self ):
        return self.content
    def is_ignore( self ):
        return self.ignore
    def __str__( self ):
        ret = ""
        if not self.ignore:
            ret = str( self.content )
        return ret


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
    def rm_node( self, node ):
        del self.nodes[node.get_name()]
        for edge in list(self.edges):
            if node in edge.get_content():
                self.edges.remove( edge )
        del self.constraint_list[node.get_name()]
        return len(self.constraint_list)
    def get_nodes( self ):
        return self.nodes
    def get_edges( self ):
        return self.edges
    def get_constraint_list( self ):
        return self.constraint_list
    def set_nodes( self, nodes ):
        self.nodes = nodes
    def set_edges( self, edges ):
        self.edges = edges
    def add_edge( self, edge ):
        self.edges.add( edge )
    def set_constraint_list( self, constraint_list ):
        self.constraint_list = constraint_list
    def get_most_constraint_node( self ):
        highest_node_cnt = -1
        most_constraint_node = None
        for node_name in self.constraint_list:
            #print "HIGHEST_NODE: " + str(highest_node_cnt) + " LIST: " + str(self.constraint_list[node_name])
            if highest_node_cnt < self.constraint_list[node_name]:
                highest_node_cnt = self.constraint_list[node_name]
                most_constraint_node = node_name
        #print "-HIGHEST_NODE: " + str(highest_node_cnt) + " LIST: " + str(most_constraint_node)
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
    def __init__( self, content, color=None ):
        self.content = content
        self.color = color
        self.active = True
    def get_content( self ):
        return self.content
    def get_color( self ):
        return self.color
    def get_name( self ):
        node_name = self.content.get_name()
        return node_name.replace( '$', '' )
    def set_color( self, color ):
        self.color = color
    def set_active( self, active ):
        self.active = active
    def is_active( self ):
        return self.active
    def get_dot_attr( self ):
        ret = ""
        if (self.color is not None) and isinstance( self.content, ASM_v_register ):
            ret = self.get_name() + " [label=\"" + self.get_name() + " [" + self.color.get_name() + "]\", color=\"" + self.color.get_color() + "\"];\n"
        elif (self.color is not None) and isinstance( self.content, ASM_register ):
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


## P0 compiler implementation
#############################
class Engine( object ):
    def __init__( self, filepath=None, DEBUG=False, PSEUDO=False ):
        self.DEBUGMODE = DEBUG
        self.PSEUDO = PSEUDO
        if filepath:
            if not os.path.exists( filepath ):
                die( "ERROR: file '%s' does not exist" % filepath )
            else:
                try:
                    ## provided AST
                    self.ast = compiler.parseFile( filepath )
                except SyntaxError:
                    die( "ERROR: invalid syntax in file '%s'" %filepath )
        self.var_counter = 0
        self.tempvar = "temp$"

        ## data structures
        self.flat_ast = []
        self.expr_list = []
        self.reg_list = {
            'eax':ASM_register('eax', True, 'red'),
            'ebx':ASM_register('ebx', False),
            'ecx':ASM_register('ecx', True, 'blue'),
            'edx':ASM_register('edx', True, 'green'),
            'edi':ASM_register('edi', False),
            'esi':ASM_register('esi', False),
            'ebp':ASM_register('ebp', False),
            'esp':ASM_register('esp', False)
        }
        ## list handling
        self.asmlist_mem = 0
        self.asmlist_vartable = {}
        self.asmlist_stack = {}

    def compileme( self, expression=None, flatten=True ):
        if expression:
            self.ast = compiler.parse( expression )

        if flatten:
            self.flat_ast = self.flatten_ast( self.ast )
        self.expr_list = self.flatten_ast_2_list( self.flat_ast, [] )

    def check_plain_integer( self, val ):
        if type( val ) is not int:
            die( "ERROR: syntax error, no plain integer allowed" )
        return val


    ## generate flatten AST
    #######################
    def flatten_ast( self, node ):
        if isinstance( node, compiler.ast.Module):
            self.DEBUG( "Module" )
            self.flat_ast = compiler.ast.Module( None, self.flatten_ast(node.node) )
            return self.flat_ast

        elif isinstance( node, compiler.ast.Stmt):
            self.DEBUG( "Stmt" )
            for n in node.nodes:
                self.flatten_ast(n)
            return compiler.ast.Stmt(self.flat_ast)

        elif isinstance(node, compiler.ast.Add):
            self.DEBUG( "Add" )
            expr = compiler.ast.Add( (self.flatten_ast(node.left), self.flatten_ast(node.right)) )
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name( new_varname )

        elif isinstance(node, compiler.ast.Mul ):
            self.DEBUG( "Mul" )
            expr = compiler.ast.Mul( (self.flatten_ast( node.left ), self.flatten_ast( node.right )) )
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name( new_varname )

        elif isinstance(node, compiler.ast.Sub ):
            self.DEBUG( "Sub" )
            expr = compiler.ast.Sub( (self.flatten_ast( node.left ), self.flatten_ast( node.right )) )
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name( new_varname )

        elif isinstance(node, compiler.ast.Const):
            self.DEBUG( "Const" )
            val = self.check_plain_integer(node.value)
            return compiler.ast.Name( self.flatten_ast_add_assign( compiler.ast.Const(val) ) )

        elif isinstance(node, compiler.ast.Discard):
            self.DEBUG( "Discard" )
            expr = self.flatten_ast( node.expr )
            new_varname = self.flatten_ast_add_assign( expr )
            return

        elif isinstance(node, compiler.ast.AssName ):
            self.DEBUG( "AssName" )
            return node

        elif isinstance( node, compiler.ast.Assign ):
            self.DEBUG( "Assign" )
            nodes = self.flatten_ast( node.nodes[0] )
            expr = self.flatten_ast( node.expr )
            self.flat_ast.append( compiler.ast.Assign( [nodes], expr ) )
            return

        elif isinstance( node, compiler.ast.Name ):
            self.DEBUG( "Name" )
            expr = compiler.ast.Name(node.name)
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.CallFunc ):
            self.DEBUG( "CallFunc" )
            expr = compiler.ast.CallFunc( node.node, [])
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Printnl ):
            self.DEBUG( "Printnl" )
            ## create a CallFunc AST with name 'print'
            attr = []
            if len(node.nodes) is not 0:
                attr = [self.flatten_ast( node.nodes[0] )]
            expr = compiler.ast.CallFunc(compiler.ast.Name('print_int_nl'), attr )
            self.flatten_ast_add_assign( expr )
            ## returns nothing because print has no return value
            return

        elif isinstance( node, compiler.ast.UnarySub ):
            self.DEBUG( "UnarySub" )
            expr = compiler.ast.UnarySub(self.flatten_ast(node.expr))
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.UnaryAdd ):
            self.DEBUG( "UnaryAdd" )
            ## ignore UnaryAdd node and use only its content
            expr = self.flatten_ast(node.expr)
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.LeftShift):
            self.DEBUG( "LeftShift" )
            expr = compiler.ast.LeftShift((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.RightShift):
            self.DEBUG( "RightShift" )
            expr = compiler.ast.RightShift((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.flatten_ast_add_assign( expr )
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Bitand ):
            self.DEBUG( "Bitand" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = compiler.ast.Bitand(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = compiler.ast.Bitand([compiler.ast.Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Bitor ):
            self.DEBUG( "Bitor" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = compiler.ast.Bitor(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = compiler.ast.Bitor([compiler.ast.Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Bitxor ):
            self.DEBUG( "Bitxor" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = compiler.ast.Bitxor(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = compiler.ast.Bitxor([compiler.ast.Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return compiler.ast.Name(new_varname)

        elif isinstance (node, compiler.ast.Invert ):
            self.DEBUG("Invert")
            expr = compiler.ast.Invert(self.flatten_ast(node.expr))
            new_varname = self.flatten_ast_add_assign(expr)    
            return compiler.ast.Name(new_varname)

        else:
            die( "unknown AST node" )

    ## helper for flatten_ast
    def flatten_ast_add_assign( self, expr ):
        self.var_counter += 1
        name = self.tempvar + str(self.var_counter)
        nodes = compiler.ast.AssName(name, 'OP_ASSIGN')
        self.flat_ast.append(compiler.ast.Assign([nodes], expr))
        self.DEBUG( "\t\t\tnew statement node: append Assign" + str( name ) )
        return name


    ## convert the flattened AST into a list of ASM expressions
    ###########################################################
    def flatten_ast_2_list( self, nd, asm_lst ):
        if isinstance( nd, compiler.ast.Module ):
            self.DEBUG( "Module" )
            self.flatten_ast_2_list( nd.node, [] )
            return self.expr_list

        elif isinstance( nd, compiler.ast.Stmt ):
            self.DEBUG( "Stmt" )
            if not self.PSEUDO:
                ## asm prolog
                self.expr_list.append( ASM_text("text") )
                self.expr_list.append( ASM_label("LC0") )
                self.expr_list.append( ASM_text("ascii \"Hello World!\"") )
                self.expr_list.append( ASM_text("globl main") )
                self.expr_list.append( ASM_label("main") )
                self.expr_list.append( ASM_pushl( self.reg_list['ebp'] ) )
                self.expr_list.append( ASM_movl( self.reg_list['esp'], self.reg_list['ebp'] ) )
                self.expr_list.append( ASM_subl( ASM_immedeate( self.init_stack_mem(0) ), self.reg_list['esp'] ) )
            ## program
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            if not self.PSEUDO:
                ## asm epilog
                self.expr_list.append( ASM_movl( ASM_stack( 0, self.reg_list['ebp'] ), self.reg_list['eax'] ) )
                self.expr_list.append( ASM_leave() )
                self.expr_list.append( ASM_ret() )
            return

        elif isinstance( nd, compiler.ast.Add ):
            self.DEBUG( "Add" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.left.name )
            right = self.lookup( nd.right.name )
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_addl( right, ret ) )
            else:
                ret = left
                self.expr_list.append( ASM_addl( right, ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Sub ):
            self.DEBUG( "Sub" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.left.name )
            right = self.lookup( nd.right.name )
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_subl( right, ret ) )
            else:
                ret = left
                self.expr_list.append( ASM_subl( right, ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Mul ):
            self.DEBUG( "Mul" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.left.name )
            right = self.lookup( nd.right.name )
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_imull( right, ret ) )
            else:
                ret = left
                self.expr_list.append( ASM_imull( right, ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Bitand ):
            self.DEBUG( "Bitand" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.nodes[0].name )
            right = self.lookup( nd.nodes[1].name )
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_andl( right, ret ) )
            else:
                ret = left
                self.expr_list.append( ASM_andl( right, ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Bitor ):
            self.DEBUG( "Bitor" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.nodes[0].name )
            right = self.lookup( nd.nodes[1].name )
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_orl( right, ret ) )
            else:
                ret = left
                self.expr_list.append( ASM_orl( right, ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Bitxor ):
            self.DEBUG( "Bitxor" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.nodes[0].name )
            right = self.lookup( nd.nodes[1].name )
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_xorl( right, ret ) )
            else:
                ret = left
                self.expr_list.append( ASM_xorl( right, ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Invert ):
            self.DEBUG( "Invert" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            op = self.lookup(nd.expr.name)
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( op, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_notl( ret ) )
            else:
                ret = op
                self.expr_list.append( ASM_notl( ret ) )
            return ret

        elif isinstance( nd, compiler.ast.UnarySub ):
            self.DEBUG( "UnarySub" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            op = self.lookup(nd.expr.name)
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( op, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_negl( ret ) )
            else:
                ret = op
                self.expr_list.append( ASM_negl( ret ) )
            return ret

        elif isinstance( nd, compiler.ast.LeftShift ):
            self.DEBUG( "LeftShift" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.left.name )
            right = self.lookup( nd.right.name )
            ## shift needs the shifting value in the register ecx
            ## and is called with %cl
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                self.expr_list.append( ASM_movl( right, self.reg_list['ecx'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_shll( ASM_register('cl'), ret ) )
            else:
                self.expr_list.append( ASM_movl( right, self.reg_list['ecx'] ) )
                ret = left
                self.expr_list.append( ASM_shll( ASM_register('cl'), ret ) )
            return ret

        elif isinstance( nd, compiler.ast.RightShift ):
            self.DEBUG( "LeftRight" )
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld, [] )
            left = self.lookup( nd.left.name )
            right = self.lookup( nd.right.name )
            ## shift needs the shifting value in the register ecx
            ## and is called with %cl
            if not self.PSEUDO:
                self.expr_list.append( ASM_movl( left, self.reg_list['eax'] ) )
                self.expr_list.append( ASM_movl( right, self.reg_list['ecx'] ) )
                ret = self.reg_list['eax']
                self.expr_list.append( ASM_shrl( ASM_register('cl'), ret ) )
            else:
                self.expr_list.append( ASM_movl( right, self.reg_list['ecx'] ) )
                ret = left
                self.expr_list.append( ASM_shrl( ASM_register('cl'), ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Assign ):
            self.DEBUG( "Assign" )
            nam = nd.nodes[0].name ## just consider the first assignement variable
            new_def_elem = self.lookup( nam, False )
            if isinstance( nd.expr, compiler.ast.Const ):
                self.expr_list.append( ASM_movl( ASM_immedeate(nd.expr.value), new_def_elem ) )
            elif isinstance( nd.expr, compiler.ast.Name ):
                ## expr is a var, in list
                if not self.PSEUDO:
                    self.expr_list.append( ASM_movl( self.stack_lookup( nd.expr.name ), self.reg_list['eax'] ) )
                    self.expr_list.append( ASM_movl( self.reg_list['eax'], new_def_elem ) )
                else:
                    self.expr_list.append( ASM_movl( self.vartable_lookup( nd.expr.name ), new_def_elem ) )
            else:
                ## expr is not const
                op = self.flatten_ast_2_list( nd.expr, [] )
                self.expr_list.append( ASM_movl( op, new_def_elem ) )
            if new_def_elem.is_new():
                self.expr_list.append( ASM_movl( new_def_elem, self.stack_lookup( new_def_elem.get_name(), False ) ) )
                new_def_elem.set_new( False )
            return

        elif isinstance( nd, compiler.ast.CallFunc ):
            self.DEBUG( "CallFunc" )
            ## lhs is name of the function
            ## rhs is name of the temp var for the param tree
            if nd.args:
                if not self.PSEUDO:
                    self.expr_list.append( ASM_movl( self.lookup( nd.args[0].name ), self.reg_list['eax'] ) )
                    self.expr_list.append( ASM_movl( self.reg_list['eax'], ASM_stack(0, self.reg_list['esp']) ) )
                else:
                    self.expr_list.append( ASM_movl( self.lookup( nd.args[0].name), ASM_stack(0, self.reg_list['esp']) ) )
            myCallObj = ASM_call( nd.node.name )
            myCallObj.set_r_def( self.reg_list['eax'] )
            myCallObj.set_r_ignore( self.reg_list['eax'] )
            myCallObj.set_r_ignore( self.reg_list['ecx'] )
            myCallObj.set_r_ignore( self.reg_list['edx'] )
            self.expr_list.append( myCallObj )
            return self.reg_list['eax']

        elif isinstance( nd, compiler.ast.Discard ):
            self.DEBUG( "Discard" )
            ## discard all below
            return []

        elif isinstance( nd, compiler.ast.Name ):
            self.DEBUG( "Name" )
            ## handled by higher node
            return []
 
        elif isinstance( nd, compiler.ast.Const ):
            ## handled by higher node
            self.DEBUG( "Const" )
            return []

        elif isinstance( nd, compiler.ast.AssName ):
            ## handled by higher node
            self.DEBUG( "AssName" )
            return []

        else:
            self.DEBUG( "*** ELSE ***" )
            return []

    ## helper for flatten_ast_2_list
    def init_stack_mem( self, mem ):
        ret_mem = 0 ## stack alloc
        if 0 < mem:
            if 16 < mem:
                if 0 != (mem%16): ret_mem = 16
                ret_mem += (mem / 16) * 16
            else: ret_mem = 16
        else:
            ret_mem = 16
        return ret_mem

    def stack_lookup( self, nam, defined=True ):
        if nam not in self.asmlist_stack:
            if defined:
                die( "ERROR: variable %s was not defined" %nam )
            ## var is new -> add a new stack object to the dict
            new_elem = ASM_stack(0 - self.asmlist_mem, self.reg_list['ebp'])
            self.asmlist_mem += 4
            self.asmlist_stack.update({nam:new_elem})
        ## return stack object containing the stack pos
        return self.asmlist_stack[nam]

    def vartable_lookup( self, nam, defined=True ):
        if nam not in self.asmlist_vartable:
            if defined:
                die( "ERROR: variable %s was not defined" %nam )
            ## var is new -> add a new virtual register object to the dict
            new_elem = ASM_v_register( nam )
            self.asmlist_vartable.update({nam:new_elem})
        ## return vartable object
        v_reg = self.asmlist_vartable[nam]
        if v_reg.is_spilled() and defined:
            ## instruction call using the spilled v_reg (not defining)
            stack_pos = self.stack_lookup( v_reg.get_spilled_name() )
            new_name = self.tempvar + str(self.var_counter)
            new_elem = ASM_v_register( new_name ) ## new v_register
            self.var_counter += 1
            self.asmlist_vartable.update({new_name:new_elem})
            self.expr_list.append( ASM_movl( stack_pos, new_elem ) )
            v_reg = new_elem
        elif v_reg.is_spilled and not defined:
            ## instruction call defining the spilled v_reg
            new_name = self.tempvar + str(self.var_counter)
            v_reg.set_spilled_name( new_name ) ## indicate to the old v_reg the name of the new v_reg
            new_elem = ASM_v_register( new_name )
            self.var_counter += 1
            new_elem.set_new( True )
            v_reg = new_elem
        return v_reg

    def lookup( self, nam, defined=True ):
        if not self.PSEUDO:
            elem = self.stack_lookup( nam, defined )
        else:
            elem = self.vartable_lookup( nam, defined )
        return elem


    ## liveness analysis
    ####################
    def liveness (self):
        # live = [[self.reg_list['eax']]]
        live = [[]]
        j = 0
        last_ignores = []
        remove_ignores = False
        for i in range( len(self.expr_list), 0, -1 ):
            element = self.expr_list[i-1]
            temp_live = self.sub_def_live( element.get_r_def(), list(live[j]) )
            temp_live = self.add_use_live( element.get_r_use(), temp_live )
            if remove_ignores: ## the iteration before added no ignore elements
                temp_live = self.sub_def_live( last_ignores, temp_live )
                remove_ignores = False
            if ( len( temp_live ) > 0 and len( element.get_r_ignore() ) > 0 ):
                ## the actual live element has live variables and the asm
                ## instruction has some special register handling
                temp_live = self.add_use_live( element.get_r_ignore(), temp_live )
                remove_ignores = True
                last_ignores = element.get_r_ignore()
            live.append( temp_live )
            j += 1
        return live

    ## helper for liveness   
    def sub_def_live( self, defi, live ):
        for oper1 in defi:
            for oper2 in live:
                if oper1.get_content().get_name() == oper2.get_content().get_name():
                    live.remove( oper2 )
        return live

    def add_use_live ( self, use, live ):
        save = True
        for oper1 in use:
            for oper2 in live:
                if oper1.get_content().get_name() == oper2.get_content().get_name():
                    save = False
            if save:
                live.append( oper1 )
        return live

    def concat_live( self, live_elems ):
        my_live_str = "#live: "
        for item in live_elems:
            if not item.is_ignore():
                ## only print 'ususal' live elements
                ## (ignore the special cases e.g. with call)
                my_live_str += str( item ) + " "
        return my_live_str


    ## coloring
    ###########
    def create_ig( self, live ): ##lives is define as argument
        ig = Graph()    ## OJO ig OBJECT = GRAPH CLASS 
        d = {}    
        node_list = {}
        edge_list = []
        node_cnt_list = {}
        for registers in live: ## register are define here, and reg_live
            ## create nodes del graph
            for reg_live in registers:
                reg = reg_live.get_content()###method get_conten,object reg_live.method get_content()
                if reg.get_name() not in node_list:###method get_name ->reg_live.get_content.get_name??
                    node = Node( reg )      
                    node_list.update( {reg.get_name():node} ) ### update the list with the new node
                    ig.add_node( node ) ### object ig . method add_node graph class
                    node_cnt_list.update( {node.get_name():0} )
            ## create edges
            for reg_live1 in registers: ## reg_live1 defin here
                reg1 = reg_live1.get_content() ###method get_conten,object reg_live1.method get_content()
                for reg_live2 in registers:
                    reg2 = reg_live2.get_content()
                    node_pair = set([node_list[reg1.get_name()], node_list[reg2.get_name()]]) ##traverse all the live to do the node pair
                    if (len(node_pair) is 2) and (node_pair not in edge_list):
                        for edge_node in node_pair:
                            if( edge_node.get_name() in node_cnt_list ):
                                node_cnt_list[edge_node.get_name()] += 1
                        edge_list.append( node_pair )
                        edge = Edge( node_pair )
                        ig.add_edge( edge ) ##SENDING DATA TO THE METHOD ADD.EDGE OF THE GRAPG CLASS
        ig.set_constraint_list( node_cnt_list )
        return ig

    def color_ig( self, ig ):
        picked_node = ig.get_most_constraint_node()
        if picked_node == None:
            return True
        picked_node.set_active( False )
        if not self.color_ig( ig ):
            return False
        picked_node.set_active( True )
        picked = False
        if isinstance(picked_node.get_content(), ASM_register):
            picked_node.set_color( picked_node.get_content() )
            picked = True
        if not picked:
            for reg_name in self.reg_list:
                color = self.reg_list[reg_name]
                if color.is_caller():
                    pick = True
                    for connected_node in ig.get_connected_nodes( picked_node ):
                        if connected_node.is_active() and color == connected_node.get_color():
                            pick = False
                            break
                    if pick:
                        picked_node.set_color(color)
                        picked = True
                        break
        if not picked:
            ## spill this node
            print "Spilled " + str(picked_node)
            picked_node.get_content().set_spilled( True )
            return False
        return ig

    ## print
    ########
    def print_asm( self, expr_lst ):
        self.DEBUG('\n\n\n')
        for expr in expr_lst:
            print str( expr )

    def print_liveness( self, live ):
        j = len( self.expr_list )
        for element in self.expr_list:
            print self.concat_live( live[j] )
            print str( element )
            j -= 1
        print self.concat_live( live[j] )

    def print_ig( self, ig ): ## print the dot file
        print str(ig)
        
        


    ## debug
    ########
    def DEBUG__print_ast( self ):
        return str( self.ast )

    def DEBUG__print_flat( self ):
        return str( self.flat_ast )

    def DEBUG__print_list( self ):
        tmp = ""
        for expr in self.expr_list:
            if 0 != len( tmp ): tmp += " "
            try:
                tmp += expr.DEBUG_type
            except:
                tmp += " Elem"
        return tmp

    def DEBUG( self, text ):
        if self.DEBUGMODE: print "\t\t%s" % str( text )


## start
if 1 <= len( sys.argv[1:] ):
    DEBUG = False
    PSEUDO = False
    LIVENESS = False
    IG = False
    IG_COLOR = False
    if 1 < len( sys.argv[1:] ) and "DEBUG" in sys.argv:
        DEBUG = True 
    if 1 < len( sys.argv[1:] ) and "-pseudo" in sys.argv:
        PSEUDO = True
    if 1 < len( sys.argv[1:] ) and "-liveness" in sys.argv:
        LIVENESS = True
        PSEUDO = True
    if 1 < len( sys.argv[1:] ) and "-ig" in sys.argv:
        IG = True
        PSEUDO = True
    if 1 < len( sys.argv[1:] ) and "-ig-color" in sys.argv:
        IG = True
        PSEUDO = True
        IG_COLOR = True

    compl = Engine( sys.argv[1], DEBUG, PSEUDO )

    if DEBUG == True:
        print "AST:"
        print compl.DEBUG__print_ast( )
        print ""

        print "FLAT AST:"
        print compl.DEBUG__print_flat( )
        print ""

        print "ASM LIST:"
        print compl.DEBUG__print_list( )
        print ""

        print "len of asmlist_vartable '%d'" % len(compl.asmlist_vartable)
        print compl.asmlist_vartable

        print "len of asmlist_stack '%d'" % len(compl.asmlist_stack)
        print compl.asmlist_stack

        print "asmlist_mem '%d'" % compl.asmlist_mem

    if LIVENESS:
        compl.compileme()
        compl.print_liveness( compl.liveness() )
    elif IG_COLOR:
        ig = False
        while True:
            compl.compileme( None, False )
            ig = compl.color_ig( compl.create_ig( compl.liveness() ) )
            if ig != False:
                break
        compl.print_ig( ig )
    elif IG:
        compl.compileme()
        compl.print_ig( compl.create_ig( compl.liveness() ) )
    else:
        compl.compileme()
        compl.print_asm( compl.expr_list ) ## object that call the method, print_asm, with the argument compl.expr_list OF THE CLASS ENGINE
else:
    usage()
