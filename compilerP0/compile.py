#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Lothar Rubusch
# Josafat Piranha

"""
USAGE:
$ python ./interp.py ./input.txt

TEST:
$ python ./test_interp.py
"""

import sys
import os.path
import compiler

## abort program
def die( meng ):
    print meng
    sys.exit( -1 )




class Expression( object ):
    def __init( self ):
        self.DEBUG_type = ""
    def print_debug( self ):
        return self.DEBUG_type



class ASM_subl( Expression ):
    def __init__( self, mem=None ):
        self.DEBUG_type = "ASM_subl"
        if mem: self.mem = mem
        else: self.mem = 16
        self.asm = "        subl $%d,%%esp" % self.mem # TODO memory     
    def __str__( self ):
        return self.asm

class ASM_movl( Expression ):
    def __init__( self ):
        self.DEBUG_type = "ASM_movl"
        self.asm = "ASM - Discard TODO"
    def __str__( self ):
        return self.asm

class ASM_addl( Expression ):
    def __init__( self ):
        self.DEBUG_type = "ASM_addl"
        self.asm = "ASM - Add TODO"
    def __str__( self ):
        return self.asm

class ASM_subl( Expression ):
    def __init__( self ):
        self.DEBUG_type = "ASM_subl"
        self.asm = "ASM - Sub TODO"
    def __str__( self ):
        return self.asm

class ASM_mull( Expression ):
    def __init__( self ):
        self.DEBUG_type = "ASM_mull"
        self.asm = "ASM - Mul TODO"
    def __str__( self ):
        return self.asm

class ASM_divl( Expression ):
    def __init__( self ):
        self.DEBUG_type = "ASM_divl"
        self.asm = "ASM - Div TODO"
    def __str__( self ):
        return self.asm

class ASM_divl( Expression ):
    def __init__( self ):
        self.DEBUG_type = "ASM_divl"
        self.asm = "ASM - Div TODO"
    def __str__( self ):
        return self.asm

class ASM_negl( Expression ):
    def __init__( self ):
        self.DEBUG_type = "ASM_negl"
        self.asm = "ASM - neg TODO"
    def __str__( self ):
        return self.asm

## TODO further ASM_ classes


## P0 compiler implementation
class Engine( object ):
    def __init__( self, filepath=None, DEBUG=False ):
        if filepath:
            if not os.path.exists( filepath ):
                die( "ERROR: file '%s' does not exist" % filepath )
            else:
                try:
                    ## provided AST
                    self.ast = compiler.parseFile( filepath )
                except SyntaxError:
                    die( "ERROR: invalid syntax in file '%s'" %filepath )

        if DEBUG: self.DEBUGMODE=True
        else: self.DEBUGMODE=False

        ## working stack
        self.stack = []

        ## last element, removed from stack
        self.ans = ''

        ## lookup table for symbols
        self.vartable = {'input':'input'}

        self.var_counter = 0

        self.flat_ast = []
        self.expr_list = []

        self.asm_prefix = """
        .text
LC0:
        .ascii "Hello, world!\10\0"
.globl main
main:
        pushl %ebp
        movl %esp, %ebp
"""

        self.asm_postfix = """
        leave
        ret
"""

    def compileme( self, expression=None ):
        if expression:
            self.ast = compiler.parse( expression )

        self.flat_ast = self.flatten_ast( self.ast )
        self.expr_list = self.flatten_ast_2_list( self.flat_ast, [] )
#        self.print_asm( self.expr_list )

    def check_plain_integer( self, val ):
        if type( val ) is not int:
            die( "ERROR: syntax error, no plain integer allowed" )
        return val

    def print_asm( self, expr_lst ):
        print ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        print self.asm_prefix
        tmp = ""
        for expr in expr_lst:
            tmp += str( expr.print_debug() )
            print str( expr )
        print self.asm_postfix
        print ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        print ""

    def flatten_ast_add_assign( self, expr ):
        self.var_counter += 1
        name = 't' + str(self.var_counter)
        nodes = compiler.ast.AssName(name, 'OP_ASSIGN')
        self.flat_ast.append(compiler.ast.Assign([nodes], expr))
        return name

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
            expr = compiler.ast.Add((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.flatten_ast_add_assign( expr )
            print "Add: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Mul ):
            self.DEBUG( "Mul" )
            expr = compiler.ast.Mul((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.flatten_ast_add_assign( expr )
            print "Mul: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Sub ):
            self.DEBUG( "Sub" )
            expr = compiler.ast.Sub((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.flatten_ast_add_assign( expr )
            print "Sub: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Const):
            self.DEBUG( "Const" )
            expr = compiler.ast.Const(node.value)
            new_varname = self.flatten_ast_add_assign( expr )
            print "Const: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Discard):
            self.DEBUG( "Discard" )
            return

        elif isinstance(node, compiler.ast.AssName ):
            self.DEBUG( "AssName" )
            return node

        elif isinstance( node, compiler.ast.Assign ):
            self.DEBUG( "Assign" )
            nodes = self.flatten_ast( node.nodes[0] )
            expr = self.flatten_ast( node.expr )
            self.flat_ast.append( compiler.ast.Assign( [nodes], expr ) )
            print "Assign: new code line, append Assign"
            return

        elif isinstance( node, compiler.ast.Name ):
            self.DEBUG( "Name" )
            expr = compiler.ast.Name( node.name )
            new_varname = self.flatten_ast_add_assign( expr )
            print "Name: new code line, append Assign", new_varname
            return compiler.ast.Name( new_varname )

        elif isinstance( node, compiler.ast.CallFunc ):
            self.DEBUG( "CallFunc" )
            expr = compiler.ast.CallFunc(self.flatten_ast(node.node), [])
            new_varname = self.flatten_ast_add_assign( expr )
            print "CallFunc: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Printnl ):
            self.DEBUG( "Printnl" )
            self.flat_ast.append(compiler.ast.Printnl(self.flatten_ast(node.nodes[0]), None))
            print "Printnl: new code line, append Printnl"
            return

        elif isinstance( node, compiler.ast.UnarySub ):
            self.DEBUG( "UnarySub" )
            expr = compiler.ast.UnarySub(self.flatten_ast(node.expr))
            new_varname = self.flatten_ast_add_assign( expr )
            print "UnarySub: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.UnaryAdd ):
            self.DEBUG( "UnaryAdd" )
            expr = compiler.ast.UnaryAdd(self.flatten_ast(node.expr))
            new_varname = self.flatten_ast_add_assign( expr )
            print "UnaryAdd: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Bitand ):
            self.DEBUG( "Bitand" )
            flat_nodes = []
            for n in node.nodes:
                flat_nodes.append(self.flatten_ast(n))
            expr = compiler.ast.Bitand(flat_nodes)
            new_varname = self.flatten_ast_add_assign( expr )
            print "Bitand: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Bitor ):
            self.DEBUG( "Bitor" )
            pass

        elif isinstance( node, compiler.ast.Bitxor ):
            self.DEBUG( "Bitxor" )
            pass

        else:
            die( "unknown AST node" )


    ## return ast_list
    def flatten_ast_2_list( self, node, ast_lst ):    
        if isinstance( node, compiler.ast.Module ):
            self.DEBUG( "Module" )
            ast_lst += self.flatten_ast_2_list( node.node, [] )  
            return ast_lst

        elif isinstance( node, compiler.ast.Stmt ):
            self.DEBUG( "Stmt" )
            tmp_lst = []
#            for child_node in node.getChildren():
#                tmp_lst += self.flatten_ast_2_list( child_node, [] )
                ## TODO translation  
                ## TODO mem calculation, to be passed to ASM_subl()   
            ast_lst += [ ASM_subl() ]
            ast_lst += tmp_lst
            return ast_lst

        elif isinstance( node, compiler.ast.Discard ):
            self.DEBUG( "Discard" )
            for child_node in node.getChildren():
                ast_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += [ ] # TODO    
            return ast_lst


        elif isinstance( node, compiler.ast.Add ):
            self.DEBUG( "Add" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [ ] # TODO exceptions     
            return ast_lst

        elif isinstance( node, compiler.ast.Sub ):
            self.DEBUG( "Sub" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [ ] # TODO     
            return ast_lst

        elif isinstance( node, compiler.ast.Mul ):
            self.DEBUG( "Mul" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [ ] # TODO   
            return ast_lst

        elif isinstance( node, compiler.ast.Div ):
            self.DEBUG( "Div" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [] # TODO   
            return ast_lst

        elif isinstance( node, compiler.ast.Bitand ):
            self.DEBUG( "Bitand" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
#            ast_lst += [ Expr_Bitand( tmp_lst[0], tmp_lst[1] ) ]
            ast_lst += [ Expr_Bitand() ]
            return ast_lst

        elif isinstance( node, compiler.ast.Bitor ):
            self.DEBUG( "Bitor" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
#            ast_lst += [ Expr_Bitor( tmp_lst[0], tmp_lst[1] ) ]
            ast_lst += [ Expr_Bitor() ]
            return ast_lst

        elif isinstance( node, compiler.ast.Bitxor ):
            self.DEBUG( "Bitxor" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
#            ast_lst += [ Expr_Bitxor( tmp_lst[0], tmp_lst[1] ) ]
            ast_lst += [ Expr_Bitxor() ]
            return ast_lst

        elif isinstance( node, compiler.ast.Const ):
            self.DEBUG( "Const" )
            ## TODO terminal
            ast_lst += [ Expr_Const( self.check_plain_integer( node.value ) ) ]
            return ast_lst

        elif isinstance(node, compiler.ast.AssName ):
            self.DEBUG( "AssName" )
            ## TODO terminal
            ast_lst += [ Expr_AssName( node.getChildren()[0] ) ]
            return ast_lst

        elif isinstance( node, compiler.ast.Assign ):
            self.DEBUG( "Assign" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += [ Expr_Assign() ]
            ast_lst += tmp_lst
            return ast_lst

        elif isinstance( node, compiler.ast.Name ):
            self.DEBUG( "Name" )
            # terminal
            ast_lst += [ Expr_Name( node.getChildren()[0] ) ]
            return ast_lst

        elif isinstance( node, compiler.ast.CallFunc ):
            self.DEBUG( "CallFunc - provokes 2 ELSE" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [ Expr_CallFunc( node.getChildren()[0] ) ]
            return ast_lst

        elif isinstance( node, compiler.ast.Printnl ):
            self.DEBUG( "Printnl - provokes 1 ELSE" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [ Expr_Printnl() ]
            return ast_lst

        elif isinstance( node, compiler.ast.UnarySub ):
            self.DEBUG( "UnarySub" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [ Expr_UnarySub() ]
            return ast_lst

        elif isinstance( node, compiler.ast.UnaryAdd ):
            self.DEBUG( "UnaryAdd" )
            tmp_lst = []
            for child_node in node.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            ast_lst += tmp_lst
            ast_lst += [ Expr_UnaryAdd() ]
            return ast_lst
        
        else:
            self.DEBUG( "*** ELSE ***" )
            print node
            return []  

    def DEBUG__print_ast( self ):
        return str( self.ast )

    def DEBUG__print_flat( self ):
        return str( self.flat_ast )

    def DEBUG__print_list( self ):
        tmp = ""
        for expr in self.expr_list:
            if 0 != len( tmp ): tmp += " "
            tmp += str( expr.print_debug() )
        return tmp

    def DEBUG( self, text ):
        if self.DEBUGMODE: print "\t\t%s" % str( text )


## start
if 1 == len( sys.argv[1:] ):
    compl = Engine( sys.argv[1], DEBUG=True )
    compl.compileme()

    print "AST:"
    print compl.DEBUG__print_ast( )
    print ""

    print "FLAT AST:"
    print compl.DEBUG__print_flat( )
    print ""

    print "EXPR LIST:"
    print compl.DEBUG__print_list( )
    print ""

