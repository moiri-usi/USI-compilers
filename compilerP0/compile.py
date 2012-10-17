#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Josafat Piraquive
# (Lothar Rubusch) contributer for prior steps of the projects

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
    def __init__( self, name, caller=True ):
        self.name = name
        self.caller = caller
    def get_name( self ):
        return self.name
    def is_caller(self):
        return self.caller
    def __str__( self ):
        return "%" + self.name

# virtual registers used for pseudo assembly
class ASM_v_register( object ):
    def __init__( self, name, spilled=False ):
        self.name = name
        self.spilled = spilled
    def get_name( self ):
        return self.name
    def is_spilled( self ):
        return self.spilled
    def __str__( self ):
        return self.name;

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
    def get_r_use( self ):
        return self.r_use
    def get_r_def( self ):
        return self.r_def
    def set_r_use( self, var ):
        if isinstance( var, ASM_v_register ) or isinstance( var, ASM_register ):
            self.r_use.append( var )
    def set_r_def( self, var ):
        if isinstance( var, ASM_v_register ) or isinstance( var, ASM_register ):
            self.r_def.append( var )
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
        self.set_r_def( ASM_register('eax') )
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
        self.tempvar = "$temp"

        ## data structures
        self.flat_ast = []
        self.expr_list = []
        self.reg_list = {
            'eax':ASM_register('eax'),
            'ebx':ASM_register('ebx', False),
            'ecx':ASM_register('ecx'),
            'edx':ASM_register('edx'),
            'edi':ASM_register('edi', False),
            'esi':ASM_register('esi', False),
            'ebp':ASM_register('ebp'),
            'esp':ASM_register('esp')
        }
        ## list handling
        self.asmlist_mem = 0
        self.asmlist_vartable = {}
        self.asmlist_stack = {}

    def compileme( self, expression=None ):
        if expression:
            self.ast = compiler.parse( expression )

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
            return compiler.ast.Name( self.flatten_ast_add_assign( compiler.ast.Const(node.value) ) )

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
                ret = right
                self.expr_list.append( ASM_addl( left, ret ) )
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
                ret = right
                self.expr_list.append( ASM_subl( left, ret ) )
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
                ret = right
                self.expr_list.append( ASM_imull( left, ret ) )
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
                ret = right
                self.expr_list.append( ASM_andl( left, ret ) )
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
                ret = right
                self.expr_list.append( ASM_orl( left, ret ) )
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
                ret = right
                self.expr_list.append( ASM_xorl( left, ret ) )
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
                self.expr_list.append( ASM_movl( left, self.reg_list['ecx'] ) )
                ret = right
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
                self.expr_list.append( ASM_movl( left, self.reg_list['ecx'] ) )
                ret = right
                self.expr_list.append( ASM_shrl( ASM_register('cl'), ret ) )
            return ret

        elif isinstance( nd, compiler.ast.Assign ):
            self.DEBUG( "Assign" )
            nam = nd.nodes[0].name ## just consider the first assignement variable

            if isinstance( nd.expr, compiler.ast.Const ):
                self.expr_list.append( ASM_movl( ASM_immedeate(nd.expr.value), self.lookup( nam ) ) )
            elif isinstance( nd.expr, compiler.ast.Name ):
                ## expr is a var, in list
                if not self.PSEUDO:
                    self.expr_list.append( ASM_movl( self.stack_lookup( nd.expr.name ), self.reg_list['eax'] ) )
                    self.expr_list.append( ASM_movl( self.reg_list['eax'], self.stack_lookup( nam ) ) )
                else:
                    self.expr_list.append( ASM_movl( self.vartable_lookup( nd.expr.name ), self.vartable_lookup( nam ) ) )
            else:
                ## expr is not const
                op = self.flatten_ast_2_list( nd.expr, [] )
                self.expr_list.append( ASM_movl( op, self.lookup( nam ) ) )
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
            self.expr_list.append( ASM_call(nd.node.name) )
            return self.reg_list['eax']

        elif isinstance( nd, compiler.ast.Discard ):
            self.DEBUG( "Discard" )
            ## discard all below
            return []

        elif isinstance( nd, compiler.ast.Name ):
            self.DEBUG( "Name" )
            ## handled by higher node
            return []
# 
#         elif isinstance( nd, compiler.ast.UnaryAdd ):
#             self.DEBUG( "UnaryAdd" )
#             ## treat as transparent
#             return self.flatten_ast_2_list( nd.getChildren()[0], [] )
# 
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

    def stack_lookup( self, nam ):
        if nam not in self.asmlist_stack:
            ## var is new -> add a new stack object to the dict
            new_elem = ASM_stack(0 - self.asmlist_mem, self.reg_list['ebp'])
            self.asmlist_mem += 4
            self.asmlist_stack.update({nam:new_elem})
        ## return stack object containing the stack pos
        return self.asmlist_stack[nam]

    def vartable_lookup( self, nam ):
        if nam not in self.asmlist_vartable:
            ## var is new -> add a new virtual register object to the dict
            new_elem = ASM_v_register( nam )
            self.asmlist_vartable.update({nam:new_elem})
        ## return vartable object
        return self.asmlist_vartable[nam]

    def lookup( self, nam ):
        if not self.PSEUDO:
            elem = self.stack_lookup( nam )
        else:
            elem = self.vartable_lookup( nam )
        return elem

    ## liveness analysis
    ####################
    def liveness (self):
        live = [[self.reg_list['eax']]]
        j = 0
        for i in range( len(self.expr_list), 0, -1 ):
            element = self.expr_list[i-1]
            temp_live = self.sub_def_live( element.get_r_def(), list(live[j]) )
            temp_live = self.add_use_live( element.get_r_use(), temp_live )
            live.append( temp_live )
            j += 1

        return live

    ## helper for liveness   
    def sub_def_live( self, defi, live ):
        for oper1 in defi:
            for oper2 in live:  
                if oper1.get_name() == oper2.get_name():
                    live.remove( oper2 )
        return live

    def add_use_live (self, use, live ):
        save = True
        for oper1 in use:
            for oper2 in live:
                if oper1.get_name() == oper2.get_name():
                    save = False
            if save: 
                live.append( oper1 )
        return live

    ## print
    ########
    def print_asm( self, expr_lst ):
        self.DEBUG('\n\n\n')
        for expr in expr_lst:
            print str( expr )

    def print_liveness ( self, live ):
        j = len( self.expr_list )
        for element in self.expr_list:
            myStr = ""            
            for item in live[j]:
                myStr += str( item ) + " "
            print "#live: " + myStr
            print str( element )
            j -= 1

 
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
    DEBUG = True if 1 < len( sys.argv[1:]) and  sys.argv[2] == "DEBUG" else False
    PSEUDO = True if 1 < len( sys.argv[1:]) and "-pseudo" in sys.argv else False
    LIVENESS = True if 1 < len( sys.argv[1:]) and "-liveness" in sys.argv else False
    if LIVENESS is True:
        PSEUDO = True
        
    
    compl = Engine( sys.argv[1], DEBUG, PSEUDO )
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

        print "len of asmlist_stack '%d'" % len(compl.asmlist_stack)
        print compl.asmlist_stack

        print "asmlist_mem '%d'" % compl.asmlist_mem

    if LIVENESS:
        compl.print_liveness(compl.liveness())
    else:
        compl.print_asm( compl.expr_list )
else:
    usage()
