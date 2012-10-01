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

class Expression( object ):
    def __init( self ):
        # TODO
        pass

## TODO in case: Terminal_Expr and Nonterminal_Expr

class Expr_Stmt( Expression ):
    def __init__( self ):
        self.asm = "ASM - Stmt TODO"
    def __str__( self ):
        return "Expr_Stmt"

class Expr_Discard( Expression ):
    def __init__( self ):
        self.asm = "ASM - Discard TODO"
    def __str__( self ):
        return "Expr_Discard"

class Expr_Add( Expression ):
    def __init__( self, a, b ):
        self.asm = "ASM - Add TODO"
        self.src_a = a
        self.src_b = b
    def __str__( self ):
        return "Expr_Add"

class Expr_Sub( Expression ):
    def __init__( self, a, b ):
        self.asm = "ASM - Sub TODO"
        self.src_a = a
        self.src_b = b
    def __str__( self ):
        return "Expr_Sub"

class Expr_Mul( Expression ):
    def __init__( self, a, b ):
        self.asm = "ASM - Mul TODO"
        self.src_a = a
        self.src_b = b
    def __str__( self ):
        return "Expr_Mul"

class Expr_Div( Expression ):
    def __init__( self, a, b ):
        self.asm = "ASM - Div TODO"
        self.src_a = a
        self.src_b = b
    def __str__( self ):
        return "Expr_Div"

class Expr_Bitand( Expression ):
    def __init__( self, a, b ):
        self.asm = "ASM - Bitand TODO"
        self.src_a = a
        self.src_b = b
    def __str__( self ):
        return "Expr_Bitand"

class Expr_Bitor( Expression ):
    def __init__( self, a, b ):
        self.asm = "ASM - Bitor TODO"
        self.src_a = a
        self.src_b = b
    def __str__( self ):
        return "Expr_Bitor"

class Expr_Bitxor( Expression ):
    def __init__( self, a, b ):
        self.asm = "ASM - Bitxor TODO"
        self.src_a = a
        self.src_b = b
    def __str__( self ):
        return "Expr_Bitxor"

class Expr_Const( Expression ):
    def __init__( self, val ):
        self.asm = "ASM - Const TODO"
        self.val = val
    def __str__( self ):
        return "Expr_Const(%s)" % self.val
    def __repr__( self ):
        return self.val

class Expr_AssName( Expression ):
    def __init__( self, val ):
        self.asm = "ASM - AssName TODO"
        self.val = val
    def __str__( self ):
        return "Expr_AssNames(%s)" % str( self.val )

class Expr_Assign( Expression ):
    def __init__( self,  ):
        self.asm = "ASM - Assign TODO"
    def __str__( self ):
        return "Expr_Assign"

class Expr_Name( Expression ):
    def __init__( self, nam ):
        self.asm = "ASM - Name TODO"
        self.nam = nam
    def __str__( self ):
        return "Expr_Name"

class Expr_CallFunc( Expression ):
    def __init__( self, fnc ):
        self.asm = "ASM - CallFunc TODO"
        self.fnc = fnc    
    def __str__( self ):
        return "Expr_CallFunc"

class Expr_Printnl( Expression ):
    def __init__( self ):
        self.asm = "ASM - Printnl TODO"
    def __str__( self ):
        return "Expr_Printnl"

class Expr_UnarySub( Expression ):
    def __init__( self ):
        self.asm = "ASM - UnarySub TODO"
    def __str__( self ):
        return "Expr_UnarySub"

class Expr_UnaryAdd( Expression ):
    def __init__( self ):
        self.asm = "ASM - UnaryAdd TODO"
    def __str__( self ):
        return "Expr_UnaryAdd"


## P0 compiler implementation
class Engine( object ):
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
        self.vartable = {'input':'input'}

        self.var_counter = 0

        self.flat_ast = []

    def compile_file( self, expression=None ):
        if expression:
            self.ast = compiler.parse( expression )

        # try:                        
        return self.flatten_ast( self.ast )
        # except AttributeError:
        #     ## specific case: TEST mode starts class without providing a P0 code
        #     ## file, so there won't be an AST already available here
        #     die( "ERROR: class started in TEST mode, no AST file set" )

    def stack_push( self, elem):
        self.stack.append( elem )

    def stack_pop( self ):
        try:
            val = self.stack.pop()
        except IndexError:
            die( "ERROR: stack index out of bounds" )
        self.ans = str( val )
        return val

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

    # TODO  
    def num_child_nodes( self, node ):
        num = sum([self.num_nodes( x ) for x in node.getChildNodes()])
        return num

    def gen_varname( self ):
        self.var_counter += 1
        print "new var t%d" %self.var_counter
        return 't' + str(self.var_counter)

    ## function to interprete the ast
    ## @param obj node: node of the ast
    # TODO 
    def num_nodes(self, node):
        return 1 + self.num_child_nodes(node);

    ## function to flatten the ast
    ## @param obj node: node of the ast
    def flatten_ast(self, node):
        if isinstance( node, compiler.ast.Module):
            print "\t\t\tModule"
            return self.flatten_ast(node.node)

        elif isinstance( node, compiler.ast.Stmt):
            print "\t\t\tStmt"
            for n in node.nodes:
                self.flatten_ast(n)
            return compiler.ast.Stmt(self.flat_ast)

        elif isinstance(node, compiler.ast.Add):
            print "\t\t\tAdd"
            expr = compiler.ast.Add((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Add: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Mul ):
            print "\t\t\tMul"
            expr = compiler.ast.Mul(self.flatten_ast(node.left), self.flatten_ast(node.right))
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Mul: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Sub ):
            print "\t\t\tSub"
            expr = compiler.ast.Sub(self.flatten_ast(node.left), self.flatten_ast(node.right))
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Sub: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Div ):
            print "\t\t\tDiv"
            expr = compiler.ast.Div(self.flatten_ast(node.left), self.flatten_ast(node.right))
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Div: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Const):
            print "\t\t\tConst"
            return node

        elif isinstance(node, compiler.ast.Discard):
            print "\t\t\tDiscard"
            return

        elif isinstance(node, compiler.ast.AssName ):
            print "\t\t\tAssName"
            return node

        elif isinstance( node, compiler.ast.Assign ):
            print "\t\t\tAssign"
            nodes = self.flatten_ast(node.nodes[0])
            expr = self.flatten_ast(node.expr)
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Assign: new code line, append Assign"
            return

        elif isinstance( node, compiler.ast.Name ):
            print "\t\t\tName"
            return node

        elif isinstance( node, compiler.ast.CallFunc ):
            print "\t\t\tCallFunc"
            expr = compiler.ast.CallFunc(self.flatten_ast(node.node), [])
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "CallFunc: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Printnl ):
            print "\t\t\tPrintnl"
            self.flat_ast.append(compiler.ast.Printnl(self.flatten_ast(node.nodes[0]), None))
            print "Printnl: new code line, append Printnl"
            return

        elif isinstance( node, compiler.ast.UnarySub ):
            print "\t\t\tUnarySub"
            return compiler.ast.UnarySub(self.flatten_ast(node.expr))

        elif isinstance( node, compiler.ast.UnaryAdd ):
            print "\t\t\tUnaryAdd"
            return compiler.ast.UnaryAdd(self.flatten_ast(node.expr))

        elif isinstance( node, compiler.ast.Bitand ):
            print "\t\t\tBitand"
            pass

        elif isinstance( node, compiler.ast.Bitor ):
            print "\t\t\tBitor"
            pass

        elif isinstance( node, compiler.ast.Bitxor ):
            print "\t\t\tBitxor"
            pass

        else:
            die( "unknown AST node" )


    ## function to compile a flatten ast 
    ## @param obj node: node of the ast
    def compile(self, node):
        pass

## start
if 1 == len( sys.argv[1:] ):
    compl = Engine( sys.argv[1] )
    compl.compile_file()
    print "AST:", compl.ast
    print "FLAT_AST:", compl.flat_ast
