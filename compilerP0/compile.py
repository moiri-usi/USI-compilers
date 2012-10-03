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


class ASM_start( Expression ):
    def __init__( self, mem=0 ):
        self.DEBUG_type = "ASM_start"
        ## lowest position on stack
        self.stack = mem
        ## stack alloc
        self.mem = 0
        if 0 < mem:
            if 16 < mem:
                if 0 != (mem%16): self.mem = 16
                self.mem += (mem / 16) * 16
            else: self.mem = 16
        else:
            self.mem = 16

    def stackconfig( self, stacksize ):
        self.asm = "        .text\n"
        self.asm += "LC0:\n"
        self.asm += '        .ascii "Hello, world!\10\0"\n'
        self.asm += ".globl main\n"
        self.asm += "main:\n"
        self.asm += "        pushl %ebp\n"
        self.asm += "        movl %esp, %ebp\n"
        self.asm += "        subl $%d, %%esp\n" % self.mem
    def __str__( self ):
        return self.asm



class ASM_end( Expression ):
    def __init__( self, mem=0 ):
        self.DEBUG_type = "ASM_end"
        self.stackpos = mem # TODO stack mech
    def stackconfig( self, stacksize ):
        self.stackpos = stacksize + 4 - self.stackpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.stackpos
        self.asm += "        leave\n"
        self.asm += "        ret\n"
    def __str__( self ):
        return self.asm


class ASM_movl_to_stack( Expression ):
    def __init__( self, pos, val=None ):
        self.DEBUG_type = "ASM_movl_to_stack"
        self.stackpos = pos
        self.val = val

    def stackconfig( self, stacksize ):
        self.stackpos = stacksize + 4 - self.stackpos
        if self.val:
            self.asm = "        movl $%d, -%d(%%ebp)" % (self.val, self.stackpos)
        else:
            self.asm = "        movl %%eax, -%d(%%ebp)" % self.stackpos

    def __str__( self ):
        return self.asm

class ASM_movl_from_stack( Expression ):
    def __init__( self, srcpos ):
        self.DEBUG_type = "ASM_movl_to_stack"
        self.stackpos = srcpos

    def stackconfig( self, stacksize ):
        self.stackpos = stacksize + 4 - self.stackpos
        self.asm = "        movl -%d(%%ebp), %%eax" % self.stackpos

    def __str__( self ):
        return self.asm

class ASM_addl( Expression ):
    def __init__( self, apos, bpos ):
        self.DEBUG_type = "ASM_addl"
        self.apos = apos
        self.bpos = bpos

    def stackconfig( self, stacksize ):
        self.apos = stacksize + 4 - self.apos
        self.bpos = stacksize + 4 - self.bpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.apos
        self.asm += "        addl -%d(%%ebp), %%eax\n" % self.bpos

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

        self.var_counter = 0

        ## data structures
        self.flat_ast = []
        self.expr_list = []

        ## list handling
        self.asmlist_mem = 0
        self.asmlist_reg = ""
        self.asmlist_op = None
        self.asmlist_vartable = {}


    def compileme( self, expression=None ):
        if expression:
            self.ast = compiler.parse( expression )

        self.flat_ast = self.flatten_ast( self.ast )
        self.expr_list = self.flatten_ast_2_list( self.flat_ast, [] )

    def asmlist_vartable_index( self, nam ):
        if nam not in self.asmlist_vartable:
            ## var is new - add, then return pos
            self.asmlist_mem += 4
            self.asmlist_vartable.update({nam:self.asmlist_mem})
        ## return value, which is stack pos
        return self.asmlist_vartable[nam]

    def check_plain_integer( self, val ):
        if type( val ) is not int:
            die( "ERROR: syntax error, no plain integer allowed" )
        return val

    def gen_varname( self ):
        self.var_counter += 1
        print "new var t%d" %self.var_counter
        return 't' + str(self.var_counter)

    def print_asm( self, expr_lst ):
        print ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        tmp = ""
        for expr in expr_lst:
            tmp += str( expr.print_debug() )
            print str( expr )
        print ";;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;"
        print ""

    def flatten_ast(self, node):
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
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Add: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Mul ):
            self.DEBUG( "Mul" )
            expr = compiler.ast.Mul(self.flatten_ast(node.left), self.flatten_ast(node.right))
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Mul: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Sub ):
            self.DEBUG( "Sub" )
            expr = compiler.ast.Sub(self.flatten_ast(node.left), self.flatten_ast(node.right))
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Sub: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Div ):
            self.DEBUG( "Div" )
            expr = compiler.ast.Div(self.flatten_ast(node.left), self.flatten_ast(node.right))
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Div: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance(node, compiler.ast.Const):
            self.DEBUG( "Const" )
            return node

        elif isinstance(node, compiler.ast.Discard):
            self.DEBUG( "Discard" )
            return

        elif isinstance(node, compiler.ast.AssName ):
            self.DEBUG( "AssName" )
            return node

        elif isinstance( node, compiler.ast.Assign ):
            self.DEBUG( "Assign" )
            nodes = self.flatten_ast(node.nodes[0])
            expr = self.flatten_ast(node.expr)
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "Assign: new code line, append Assign"
            return

        elif isinstance( node, compiler.ast.Name ):
            self.DEBUG( "Name" )
            return node

        elif isinstance( node, compiler.ast.CallFunc ):
            self.DEBUG( "CallFunc" )
            expr = compiler.ast.CallFunc(self.flatten_ast(node.node), [])
            new_varname = self.gen_varname()
            nodes = compiler.ast.AssName(new_varname, 'OP_ASSIGN')
            self.flat_ast.append(compiler.ast.Assign([nodes], expr))
            print "CallFunc: new code line, append Assign", new_varname
            return compiler.ast.Name(new_varname)

        elif isinstance( node, compiler.ast.Printnl ):
            self.DEBUG( "Printnl" )
            self.flat_ast.append(compiler.ast.Printnl(self.flatten_ast(node.nodes[0]), None))
            print "Printnl: new code line, append Printnl"
            return

        elif isinstance( node, compiler.ast.UnarySub ):
            self.DEBUG( "UnarySub" )
            return compiler.ast.UnarySub(self.flatten_ast(node.expr))

        elif isinstance( node, compiler.ast.UnaryAdd ):
            self.DEBUG( "UnaryAdd" )
            return compiler.ast.UnaryAdd(self.flatten_ast(node.expr))

        elif isinstance( node, compiler.ast.Bitand ):
            self.DEBUG( "Bitand" )
            pass

        elif isinstance( node, compiler.ast.Bitor ):
            self.DEBUG( "Bitor" )
            pass

        elif isinstance( node, compiler.ast.Bitxor ):
            self.DEBUG( "Bitxor" )
            pass

        else:
            die( "unknown AST node" )


    ## return ast_list
    # TODO order
    # TODO mem counter
    def flatten_ast_2_list( self, nd, asm_lst ):    
        if isinstance( nd, compiler.ast.Module ):
            self.DEBUG( "Module" )
            asm_lst += self.flatten_ast_2_list( nd.node, [] )  
            return asm_lst

        elif isinstance( nd, compiler.ast.Stmt ):
            self.DEBUG( "Stmt" )
            lst = []
            self.asmlist_op = None
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )

            asm_lst += [ ASM_start( self.asmlist_mem ) ] ## alloc space on stack
            asm_lst += lst
            asm_lst += [ ASM_end( self.asmlist_mem ) ]
            for item in asm_lst: item.stackconfig( self.asmlist_mem)
            return asm_lst

        elif isinstance( nd, compiler.ast.Discard ):
            self.DEBUG( "Discard" )
            asm_lst += [ ]
            return asm_lst


        elif isinstance( nd, compiler.ast.Add ):
            self.DEBUG( "Add" )

            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )

            asm_lst += lst
            asm_lst += [ ASM_addl( self.asmlist_vartable_index( nd.left.name ), self.asmlist_vartable_index( nd.right.name ) ) ]

            return asm_lst


        elif isinstance( nd, compiler.ast.Sub ):
            
            self.DEBUG( "Sub" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ ] # TODO     
            return asm_lst

        elif isinstance( nd, compiler.ast.Mul ):
            
            self.DEBUG( "Mul" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ ] # TODO   
            return asm_lst

        elif isinstance( nd, compiler.ast.Bitand ):
            
            self.DEBUG( "Bitand" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ Expr_Bitand() ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Bitor ):
            
            self.DEBUG( "Bitor" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ Expr_Bitor() ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Bitxor ):
            
            self.DEBUG( "Bitxor" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ Expr_Bitxor() ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Const ):
            ## upper node is handling
            self.DEBUG( "Const" )
            return asm_lst

        elif isinstance( nd, compiler.ast.AssName ):
            ## upper node is handling
            self.DEBUG( "AssName" )
            return []


        elif isinstance( nd, compiler.ast.Assign ):
            self.DEBUG( "Assign" )

            ## lhs is var
            nam = nd.getChildren()[0].name
            lst = []

            ## rhs is const
            if isinstance( nd.getChildren()[1], compiler.ast.Const ):
                val = nd.getChildren()[1].value
                stackpos = self.asmlist_vartable_index( nam )
                lst = [ ASM_movl_to_stack( stackpos, val ) ]

            elif isinstance( nd.getChildren()[1], compiler.ast.Name ):
                ## rhs is a var, in list
                srcnam = nd.getChildren()[1].name
                srcpos = self.asmlist_vartable_index( srcnam )
                dstpos = self.asmlist_vartable_index( nam )
                lst = [ ASM_movl_from_stack( srcpos ), ASM_movl_to_stack( dstpos ) ]

            else:
                ## rhs is not const
                ## else take %eax
                lst = self.flatten_ast_2_list( nd.getChildren()[1], [] )
                stackpos = self.asmlist_vartable_index( nam )
                lst += [ ASM_movl_to_stack( stackpos ) ]


            asm_lst += lst

            return asm_lst


        elif isinstance( nd, compiler.ast.Name ):
            self.DEBUG( "Name" )
            self.asmlist_vartable_index( nd.name )

            return []

        elif isinstance( nd, compiler.ast.CallFunc ):
            
            self.DEBUG( "CallFunc" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ Expr_CallFunc( nd.getChildren()[0] ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Printnl ):
            
            self.DEBUG( "Printnl" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ Expr_Printnl() ]
            return asm_lst

        elif isinstance( nd, compiler.ast.UnarySub ):
            
            self.DEBUG( "UnarySub" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ Expr_UnarySub() ]
            return asm_lst

        elif isinstance( nd, compiler.ast.UnaryAdd ):
            
            self.DEBUG( "UnaryAdd" )
            tmp_lst = []
            for child_node in nd.getChildren():
                tmp_lst += self.flatten_ast_2_list( child_node, [] )
            asm_lst += tmp_lst
            asm_lst += [ Expr_UnaryAdd() ]
            return asm_lst
        
        else:
            
            self.DEBUG( "*** ELSE ***" )
            print nd
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

    print "ASM LIST:"
    print compl.DEBUG__print_list( )
    print ""

    compl.print_asm( compl.expr_list )

    print "len of asmlist_vartable '%d'" % len(compl.asmlist_vartable)
    print compl.asmlist_vartable
