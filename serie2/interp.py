#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Lothar Rubusch

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

## interpreter implementation
class Interpreterer( object ):
    def __init__( self, filepath=None ):
        if filepath:
            if not os.path.exists( filepath ):
                die( "ERROR: file '%s' does not exist" % filepath )
            else:
                try:
                    ## provided AST
                    self.ast = compiler.parseFile( filepath )
                except SyntaxError:
                    die( "ERROR: invalid syntax in file '%s'" %filepath )

        ## working stack
        self.stack = []

        ## last element, removed from stack
        self.ans = ''

        ## lookup table for symbols
        self.vartable = {}

    def interpret_file( self ):
        try:
            return self.num_nodes( self.ast )
        except AttributeError:
            ## specific case: TEST mode starts class without providing a P0 code
            ## file, so there won't be an AST already available here
            die( "ERROR: class started in TEST mode, no AST file set" )

    def stack_push( self, elem):
        self.stack.append( elem )

    def stack_pop( self ):
        try:
            val = self.stack.pop()
        except IndexError:
            die( "ERROR: stack index out of bounds" )
        self.ans = str( val )
        return val

    def stack_pop_smart( self ):
        ## get elem from stack, in case elem is a var name,
        ## look it up in vartable
        res = self.stack_pop()
        if type(res) == str:
            res = self.vartable_get(res)
        return res

    def stack_ans( self ):
        return self.ans

    def vartable_set( self, name, val ):
        self.vartable.update( {name:val} )

    def vartable_get( self, name ):
        try:
            return self.vartable[name]
        except KeyError:
            die( "ERROR: variable '%s' does not exist" % name )

    def check_plain_integer( self, val ):
        if type( val ) is not int:
            die( "ERROR: syntax error, no plain integer allowed" )
        return val


    def num_child_nodes( self, node ):
        num = sum([self.num_nodes(x) for x in node.getChildNodes()])
        return num

    ## function to interprete the ast
    ## @param obj node: node of the ast
    def num_nodes(self, node):
        if isinstance( node, compiler.ast.Module):
            self.ans = ''
            return self.num_nodes(node.node)

        elif isinstance( node, compiler.ast.Stmt):
            try:
                num = 1 + self.num_child_nodes( node )
                return num
            except:
                die( "ERROR: None Type received, corrupt node handling" )

        elif isinstance(node, compiler.ast.Add):
            num = 1 + self.num_child_nodes( node )
            self.stack_push( self.stack_pop_smart() + self.stack_pop_smart() )
            return num

        elif isinstance(node, compiler.ast.Mul ):
            num = 1 + self.num_child_nodes( node )
            self.stack_push( self.stack_pop_smart() * self.stack_pop_smart() )
            return num

        elif isinstance(node, compiler.ast.Sub ):
            num = 1 + self.num_child_nodes( node )
            var_a = self.stack_pop_smart()
            var_b = self.stack_pop_smart()
            self.stack_push( var_b - var_a )
            return num

        elif isinstance(node, compiler.ast.Div ):
            num = 1 + self.num_child_nodes( node )
            var_a = self.stack_pop_smart()
            var_b = self.stack_pop_smart()
            try:
                self.stack_push( var_b / var_a )
            except ZeroDivisionError:
                die( "ERROR: division by 0" )
            return num

        elif isinstance(node, compiler.ast.Const):
            self.stack_push( self.check_plain_integer( node.value ) )
            return 1

        elif isinstance(node, compiler.ast.Discard):
            num = 1 + self.num_child_nodes( node )
            self.stack_pop()
            return num

        elif isinstance(node, compiler.ast.AssName ):
            self.stack_push( node.name )
            self.vartable_set( node.name, -1 )
            return 1

        elif isinstance(node, compiler.ast.Assign ):
            num = 1 + self.num_child_nodes( node )
            val = self.stack_pop()
            name = self.stack_pop()
            self.vartable_set( name, val )
            return num

        elif isinstance(node, compiler.ast.Name ):
            self.stack_push( node.name )
            return 1

        elif isinstance(node, compiler.ast.CallFunc ):
            num = 1 + self.num_child_nodes( node )
            name = self.stack_pop()
            if "input" == name: self.stack_push( self.check_plain_integer( input() ) ) # well..
            return num

        elif isinstance(node, compiler.ast.Printnl ):
            num = 1 + self.num_child_nodes( node )
            print "%s" % str( self.stack_pop_smart() )
            return num

        elif isinstance(node, compiler.ast.UnarySub ):
            num = 1 + self.num_child_nodes( node )
            self.stack_push( -self.stack_pop() )
            return num

        elif isinstance(node, compiler.ast.UnaryAdd ):
            num = 1 + self.num_child_nodes( node )
            self.stack_push( +self.stack_pop() )
            return num

        elif isinstance(node, compiler.ast.Bitand ):
            num = 1 + self.num_child_nodes( node )
            self.stack_push( self.stack_pop_smart() & self.stack_pop_smart() )
            return num

        elif isinstance(node, compiler.ast.Bitor ):
            num = 1 + self.num_child_nodes( node )
            self.stack_push( self.stack_pop_smart() | self.stack_pop_smart() )
            return num

        elif isinstance(node, compiler.ast.Bitxor ):
            num = 1 + self.num_child_nodes( node )
            self.stack_push( self.stack_pop_smart() ^ self.stack_pop_smart() )
            return num

        else:
            die( "unknown AST node" )

## start
if 1 == len( sys.argv[1:] ):
    inst = Interpreterer( sys.argv[1] )
    number_of_nodes = inst.interpret_file()
