#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Lothar Rubusch
# Josafat Piraquive

"""
USAGE:
$ python ./interp.py ./input.txt

TEST:
$ python ./test_interp.py
"""

import sys
import os.path
import compiler



## auxiliary

def die( meng ):
    print meng
    sys.exit( -1 )

def usage():
    print "USAGE:"
    print "    %s <inputfile>" % sys.argv[0]
    print "or"
    print "    %s <inputfile> DEBUG" % sys.argv[0]

## ASM vat types


class ASM_register( object ):
    def __init__( self, name, caller=True ):
        self.name = name
        self.caller = caller
    def is_caller(self):
        return self.caller
    def __str__( self ):
        return "%" + self.name


class ASM_v_register( object ):
    def __init__( self, name ):
        self.name = name
    def __str__( self ):
        return self.name;


class ASM_stack( object ):
    def __init__( self, pos, stackptr ):
        self.pos = pos
        self.stackptr = stackptr
    def __str__( self ):
        pos_str = ''
        if pos != 0:
            pos_str = str(self.pos)
        return  pos_str + "(" + str(self.stackptr) + ")"


class ASM_immedeate( object ):
    def __init__(self, val ):
        self.val = val
    def __str__( self ):
        return '$%d' % self.val


## ASM Expression

class ASM_BASE( object ):
    def __init( self ):
        self.DEBUG_type = ""
    def print_debug( self ):
        return self.DEBUG_type
    def __str__( self ):
        return self.asm


class ASM_start( ASM_BASE ):
    def __init__( self, mem=0 ):
        self.DEBUG_type = "ASM_start"
        self.mem = 0 ## stack alloc
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
        self.asm += "        subl $%d, %%esp" % self.mem


class ASM_end( ASM_BASE ):
    def __init__( self, mem=0 ):
        self.DEBUG_type = "ASM_end"
        self.stackpos = mem
    def stackconfig( self, stacksize ):
        self.stackpos = stacksize + 4 - self.stackpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.stackpos
        self.asm += "        leave\n"
        self.asm += "        ret\n"


class ASM_movl_to_stack( ASM_BASE ):
    def __init__( self, pos, val=None ):
        self.DEBUG_type = "ASM_movl_to_stack"
        self.stackpos = pos
        self.val = val
    def stackconfig( self, stacksize ):
        self.stackpos = stacksize + 4 - self.stackpos
        if self.val is not None:
            self.asm = "        movl $%d, -%d(%%ebp)" % (self.val, self.stackpos)
        else:
            self.asm = "        movl %%eax, -%d(%%ebp)" % self.stackpos


class ASM_movl_from_stack( ASM_BASE ):
    def __init__( self, srcpos ):
        self.DEBUG_type = "ASM_movl_to_stack"
        self.stackpos = srcpos
    def stackconfig( self, stacksize ):
        self.stackpos = stacksize + 4 - self.stackpos
        self.asm = "        movl -%d(%%ebp), %%eax" % self.stackpos


class ASM_addl( ASM_BASE ):
    def __init__( self, apos, bpos ):
        self.DEBUG_type = "ASM_addl"
        self.apos = apos
        self.bpos = bpos
    def stackconfig( self, stacksize ):
        self.apos = stacksize + 4 - self.apos
        self.bpos = stacksize + 4 - self.bpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.apos
        self.asm += "        addl -%d(%%ebp), %%eax" % self.bpos


class ASM_subl( ASM_BASE ):
    def __init__( self, apos, bpos ):
        self.DEBUG_type = "ASM_subl"
        self.apos = apos
        self.bpos = bpos
    def stackconfig( self, stacksize ):
        self.apos = stacksize + 4 - self.apos
        self.bpos = stacksize + 4 - self.bpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.apos
        self.asm += "        subl -%d(%%ebp), %%eax" % self.bpos


class ASM_mull( ASM_BASE ):
    def __init__( self, apos, bpos ):
        self.DEBUG_type = "ASM_mull"
        self.apos = apos
        self.bpos = bpos
    def stackconfig( self, stacksize ):
        self.apos = stacksize + 4 - self.apos
        self.bpos = stacksize + 4 - self.bpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.apos
        self.asm += "        movl -%d(%%ebp), %%ebx\n" % self.bpos
        self.asm += "        mull %ebx\n"


class ASM_bitand( ASM_BASE ):
    def __init__( self, apos, bpos ):
        self.DEBUG_type = "ASM_bitand"
        self.apos = apos
        self.bpos = bpos
    def stackconfig( self, stacksize ):
        self.apos = stacksize + 4 - self.apos
        self.bpos = stacksize + 4 - self.bpos
        self.asm = "        movl -%d(%%ebp), %%ebx\n" % self.bpos
        self.asm += "        movl -%d(%%ebp), %%eax\n" % self.apos
        self.asm += "        andl %ebx, %eax"


class ASM_bitor( ASM_BASE ):
    def __init__( self, apos, bpos ):
        self.DEBUG_type = "ASM_bitor"
        self.apos = apos
        self.bpos = bpos
    def stackconfig( self, stacksize ):
        self.apos = stacksize + 4 - self.apos
        self.bpos = stacksize + 4 - self.bpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.apos
        self.asm += "        movl -%d(%%ebp), %%edx\n"  % self.bpos
        self.asm += "        orl %edx, %eax"


class ASM_bitxor( ASM_BASE ):
    def __init__( self, apos, bpos ):
        self.DEBUG_type = "ASM_bitxor"
        self.apos = apos
        self.bpos = bpos
    def stackconfig( self, stacksize ):
        self.apos = stacksize + 4 - self.apos
        self.bpos = stacksize + 4 - self.bpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.apos
        self.asm += "        movl -%d(%%ebp), %%edx\n"  % self.bpos
        self.asm += "        xorl %edx, %eax"


class ASM_negl( ASM_BASE ):
    def __init__( self, srcpos ):
        self.DEBUG_type = "ASM_negl"
        self.srcpos = srcpos
    def stackconfig( self, stacksize ):
        self.srcpos = stacksize + 4 - self.srcpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.srcpos
        self.asm += "        negl %eax"


class ASM_call( ASM_BASE ):
    def __init__( self, nam, stackpos=None ):
        self.DEBUG_type = "ASM_call"
        self.stackpos = stackpos
        self.nam = nam
        self.asm = ""
    def stackconfig( self, stacksize ):
        if self.stackpos:
            self.stackpos = stacksize + 4 - self.stackpos
            self.asm = "        movl -%d(%%ebp), %%eax\n"  % self.stackpos
            self.asm += "        movl %eax, (%esp)\n"
        self.asm += "        call %s" % self.nam


class ASM_leftshift( ASM_BASE ):
    def __init__( self, srcpos, shiftpos ):
        self.DEBUG_type = "ASM_leftshift"
        self.srcpos = srcpos
        self.shiftpos = shiftpos
    def stackconfig( self, stacksize ):
        self.srcpos = stacksize + 4 - self.srcpos
        self.shiftpos = stacksize + 4 - self.shiftpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.shiftpos
        self.asm += "        movl -%d(%%ebp), %%edx\n" % self.srcpos
        self.asm += "        movl %edx, %ebx\n"
        self.asm += "        movl %eax, %ecx\n"
        self.asm += "        shll %cl, %ebx\n"
        self.asm += "        movl %ebx, %eax"


class ASM_rightshift( ASM_BASE ):
    def __init__( self, srcpos, shiftpos ):
        self.DEBUG_type = "ASM_rightshift"
        self.srcpos = srcpos
        self.shiftpos = shiftpos
    def stackconfig( self, stacksize ):
        self.srcpos = stacksize + 4 - self.srcpos
        self.shiftpos = stacksize + 4 - self.shiftpos
        self.asm = "        movl -%d(%%ebp), %%eax\n" % self.shiftpos
        self.asm += "        movl -%d(%%ebp), %%edx\n" % self.srcpos
        self.asm += "        movl %edx, %ebx\n"
        self.asm += "        movl %eax, %ecx\n"
        self.asm += "        shrl %cl, %ebx\n"
        self.asm += "        movl %ebx, %eax"


## P0 compiler implementation
class Engine( object ):
    def __init__( self, filepath=None, DEBUG=False ):
        self.DEBUGMODE = DEBUG
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
        self.tempvar = "$temp"

        ## data structures
        self.flat_ast = []
        self.expr_list = []

        ## list handling
        self.asmlist_mem = 0
        self.asmlist_vartable = {}

    def compileme( self, expression=None ):
        if expression:
            self.ast = compiler.parse( expression )

        self.flat_ast = self.flatten_ast( self.ast )
        self.expr_list = self.flatten_ast_2_list( self.flat_ast, [] )

    def vartable_lookup( self, nam ):
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

    def print_asm( self, expr_lst ):
        self.DEBUG('\n\n\n')
        for expr in expr_lst:
            print str( expr )

    def flatten_ast_add_assign( self, expr ):
        self.var_counter += 1
        name = self.tempvar + str(self.var_counter)
        nodes = compiler.ast.AssName(name, 'OP_ASSIGN')
        self.flat_ast.append(compiler.ast.Assign([nodes], expr))
        self.DEBUG( "\t\t\tnew statement node: append Assign" + str( name ) )
        return name


    ## part 1: flatten AST
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
            return compiler.ast.Name( self.flatten_ast_add_assign( compiler.ast.Add((self.flatten_ast(node.left), self.flatten_ast(node.right))) ) )

        elif isinstance(node, compiler.ast.Mul ):
            self.DEBUG( "Mul" )
            return compiler.ast.Name( self.flatten_ast_add_assign( compiler.ast.Mul((self.flatten_ast(node.left), self.flatten_ast(node.right))) ) )

        elif isinstance(node, compiler.ast.Sub ):
            self.DEBUG( "Sub" )
            return compiler.ast.Name( self.flatten_ast_add_assign( compiler.ast.Sub((self.flatten_ast(node.left), self.flatten_ast(node.right))) ) )

        elif isinstance(node, compiler.ast.Const):
            self.DEBUG( "Const" )
            return compiler.ast.Name( self.flatten_ast_add_assign( compiler.ast.Const(node.value) ) )

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
            expr = compiler.ast.CallFunc(compiler.ast.Name('print_int_nl'), [self.flatten_ast( node.nodes[0] ) ])
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
            expr = compiler.ast.UnaryAdd(self.flatten_ast(node.expr))
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

        else:
            die( "unknown AST node" )




    ## part 2: convert the flattened AST into a list of ASM expressions
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
            asm_lst += [ ASM_start( self.asmlist_mem ) ] ## asm prolog
            asm_lst += lst
            asm_lst += [ ASM_end( self.asmlist_mem ) ] ## asm epilog
            for item in asm_lst: item.stackconfig( self.asmlist_mem )
            return asm_lst

        elif isinstance( nd, compiler.ast.Add ):
            self.DEBUG( "Add" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_addl( self.vartable_lookup( nd.left.name ), self.vartable_lookup( nd.right.name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Sub ):
            self.DEBUG( "Sub" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_subl( self.vartable_lookup( nd.left.name ), self.vartable_lookup( nd.right.name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Mul ):
            self.DEBUG( "Mul" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_mull( self.vartable_lookup( nd.left.name ), self.vartable_lookup( nd.right.name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Bitand ):
            self.DEBUG( "Bitand" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_bitand( self.vartable_lookup( nd.getChildren()[0].name ), self.vartable_lookup( nd.getChildren()[1].name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Bitor ):
            self.DEBUG( "Bitor" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_bitor( self.vartable_lookup( nd.getChildren()[0].name ), self.vartable_lookup( nd.getChildren()[1].name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Bitxor ):
            self.DEBUG( "Bitxor" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_bitxor( self.vartable_lookup( nd.getChildren()[0].name ), self.vartable_lookup( nd.getChildren()[1].name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.UnarySub ):
            self.DEBUG( "UnarySub" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_negl( self.vartable_lookup( nd.getChildren()[0].name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.LeftShift ):
            self.DEBUG( "LeftShift" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_leftshift( self.vartable_lookup( nd.getChildren()[0].name ), self.vartable_lookup( nd.getChildren()[1].name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.RightShift ):
            self.DEBUG( "RightShift" )
            lst = []
            for chld in nd.getChildren():
                lst += self.flatten_ast_2_list( chld, [] )
            asm_lst += lst
            asm_lst += [ ASM_rightshift( self.vartable_lookup( nd.getChildren()[0].name ), self.vartable_lookup( nd.getChildren()[1].name ) ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Assign ):
            self.DEBUG( "Assign" )

            ## lhs is var
            nam = nd.getChildren()[0].name
            lst = []

            ## rhs is const
            if isinstance( nd.getChildren()[1], compiler.ast.Const ):
                val = nd.getChildren()[1].value
                stackpos = self.vartable_lookup( nam )
                lst = [ ASM_movl_to_stack( stackpos, val ) ]

            elif isinstance( nd.getChildren()[1], compiler.ast.Name ):
                ## rhs is a var, in list
                lst = [ ASM_movl_from_stack( self.vartable_lookup( nd.getChildren()[1].name ) ), ASM_movl_to_stack( self.vartable_lookup( nam ) ) ]
            else:
                ## rhs is not const
                ## else take %eax as default reg
                lst = self.flatten_ast_2_list( nd.getChildren()[1], [] )
                stackpos = self.vartable_lookup( nam )
                lst += [ ASM_movl_to_stack( stackpos ) ]
            asm_lst += lst
            return asm_lst

        elif isinstance( nd, compiler.ast.CallFunc ):
            self.DEBUG( "CallFunc" )
            ## lhs is name of the function
            ## rhs is name of the temp var for the param tree
            if nd.getChildren()[1]:
                asm_lst += [ ASM_call( nd.getChildren()[0].name, self.vartable_lookup( nd.getChildren()[1].name ) ) ]
            else:
                asm_lst += [ ASM_call( nd.getChildren()[0].name ) ]
            return asm_lst

        elif isinstance( nd, compiler.ast.Discard ):
            self.DEBUG( "Discard" )
            ## discard all below
            return []

        elif isinstance( nd, compiler.ast.Name ):
            self.DEBUG( "Name" )
            ## handled by higher node
            return []

        elif isinstance( nd, compiler.ast.UnaryAdd ):
            self.DEBUG( "UnaryAdd" )
            ## treat as transparent
            return self.flatten_ast_2_list( nd.getChildren()[0], [] )

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

#    def liveness( self, v_reg_list ):
#        v_reg_live
#        v_reg_use
#        v_reg_def
#        v_reg_live(i) = (v_reg_live(i+1) - v_reg_dev) + v_reg_use
#        for i in range(v_reg_list.length, 0, -1):
#            if isinstance( v_reg_list[i].use, ASM_v_register ):
#                v_reg_use.append( v_reg_list[i].use )
             

    ## debug
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


if 1 <= len( sys.argv[1:] ):
    DEBUG = True if 1 < len( sys.argv[1:]) and  sys.argv[2] == "DEBUG" else False

    compl = Engine( sys.argv[1], DEBUG )
    compl.compileme()

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

        print "asmlist_mem '%d'" % compl.asmlist_mem

##
    compl.print_asm( compl.expr_list )
else:
    usage()
