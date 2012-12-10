#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Josafat Piraquive
# (Lothar Rubusch) contributer for prior steps of the project

import sys
import os.path
import compiler
from compiler.ast import *
from ig import *
from asm import *

## auxiliary
def die( meng ):
    print meng
    sys.exit( -1 )

def usage():
    print "USAGE:"
    print "    %s [OPERATION] [ARGUMENT] FILE" % sys.argv[0]
    print "OPERATION:"
    print "    -pseudo:   prints ASM-pseudo-code using virtual registers"
    print "    -liveness: prints the liveness analysis of the -pseudo ASM"
    print "    -ig:       prints dot syntax of the interference graph"
    print "    -ig-color: prints dot syntax of the colored interference graph"
    print "    -alloc:    prints ASM-code using register allocation (default)"
    print "ARGUMENT:"
    print "    -debug:    prints additional debug information"
    print "    -o:        optimize the assembler code"
    print "FILE:"
    print "    A file containing valid P0 code. This file is mandatory for the script to run\n"


## Additional AST Classes
#########################
class Label(Node):
    def __init__(self, name):
        self.name = name

    def getChildren(self):
        return (self.name)

    def getChildNodes(self):
        return (self.name)

class LabelName(Node):
    def __init__(self, name):
        self.name = name

    def getChildren(self):
        return (self.name)

    def getChildNodes(self):
        return ()

class Goto(Node):
    def __init__(self, label):
        self.label = label

    def getChildren(self):
        return (self.label)

    def getChildNodes(self):
        return (self.label)

class AssignBool(Node):
    def __init__(self, nodes, expr, comp):
        self.nodes = nodes
        self.expr = expr
        self.comp = comp

    def getChildren(self):
        tpl = ()
        for node in nodes:
            tpl += (node,)
        tpl += (expr,)
        tpl += (comp,)
        return tpl

    def getChildNodes(self):
        tpl = ()
        for node in nodes:
            tpl += (node,)
        tpl += (expr,)
        return tpl


## P0 compiler implementation
#############################
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
        self.tempvar = "temp$"
        self.label_counter = 0
        self.templabel = "L"

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
        self.asmlist_labeltable = {}

    def compileme( self, expression=None, flatten=True ):
        self.asmlist_mem = 0
        if expression:
            self.ast = compiler.parse( expression )
        if flatten:
            self.flat_ast = self.flatten_ast( self.ast )
        self.expr_list = []
        self.expr_list = self.flatten_ast_2_list( self.flat_ast )

    def check_plain_integer( self, val ):
        if type( val ) is not int:
            die( "ERROR: syntax error, no plain integer allowed" )
        return val


    ## generate flatten AST
    #######################
    def flatten_ast( self, node, flat_tmp=None ):
        if isinstance( node, Module):
            self.DEBUG( "Module" )
            self.flat_ast = Module( None, self.flatten_ast(node.node) )
            return self.flat_ast

        elif isinstance( node, Stmt):
            self.DEBUG( "Stmt" )
            for n in node.nodes:
                self.flatten_ast(n)
            return Stmt(self.flat_ast)

        elif isinstance(node, Add):
            self.DEBUG( "Add" )
            expr = Add( (self.flatten_ast(node.left), self.flatten_ast(node.right)) )
            new_varname = self.flatten_ast_add_assign( expr )
            return Name( new_varname )

        elif isinstance(node, Mul ):
            self.DEBUG( "Mul" )
            expr = Mul( (self.flatten_ast( node.left ), self.flatten_ast( node.right )) )
            new_varname = self.flatten_ast_add_assign( expr )
            return Name( new_varname )

        elif isinstance(node, Sub ):
            self.DEBUG( "Sub" )
            expr = Sub( (self.flatten_ast( node.left ), self.flatten_ast( node.right )) )
            new_varname = self.flatten_ast_add_assign( expr )
            return Name( new_varname )

        elif isinstance(node, Const):
            self.DEBUG( "Const" )
            val = self.check_plain_integer(node.value)
            return Name( self.flatten_ast_add_assign( Const(val) ) )

        elif isinstance(node, Discard):
            self.DEBUG( "Discard" )
            expr = self.flatten_ast( node.expr )
            new_varname = self.flatten_ast_add_assign( expr )
            return

        elif isinstance(node, AssName ):
            self.DEBUG( "AssName" )
            return node

        elif isinstance( node, Assign ):
            self.DEBUG( "Assign" )
            nodes = self.flatten_ast( node.nodes[0] )
            expr = self.flatten_ast( node.expr )
            self.flat_ast.append( Assign( [nodes], expr ) )
            return

        elif isinstance( node, Name ):
            self.DEBUG( "Name" )
            ## because of function names we need to create a new assignment
            expr = Name(node.name)
            new_varname = self.flatten_ast_add_assign( expr )
            return Name(new_varname)

        elif isinstance( node, CallFunc ):
            self.DEBUG( "CallFunc" )
            attr = []
            for attr_elem in node.args:
                attr.append( self.flatten_ast( attr_elem ) )
            expr = CallFunc( node.node, attr )
            new_varname = self.flatten_ast_add_assign( expr )
            return Name(new_varname)

        elif isinstance( node, Printnl ) or isinstance( node, Print ):
            if isinstance( node, Printnl ):
                fct_name = "print_int_nl"
                self.DEBUG( "Printnl" )
            elif isinstance( node, Print ):
                fct_name = "print_int"
                self.DEBUG( "Print" )
            ## create a CallFunc AST with name 'print_int_nl'
            attr = []
            i = 0
            for attr_elem in node.nodes:
                i += 1
                attr = [ self.flatten_ast( attr_elem ) ]
                if len( node.nodes ) > i:
                    expr = CallFunc(Name( "print_int" ), attr )
                    self.flatten_ast_add_assign( expr )
            expr = CallFunc(Name( fct_name ), attr )
            self.flatten_ast_add_assign( expr )
            ## returns nothing because print has no return value
            return

        elif isinstance( node, UnarySub ):
            self.DEBUG( "UnarySub" )
            expr = UnarySub(self.flatten_ast(node.expr))
            new_varname = self.flatten_ast_add_assign( expr )
            return Name(new_varname)

        elif isinstance( node, UnaryAdd ):
            self.DEBUG( "UnaryAdd" )
            ## ignore UnaryAdd node and use only its content
            expr = self.flatten_ast(node.expr)
            new_varname = self.flatten_ast_add_assign( expr )
            return Name(new_varname)

        elif isinstance(node, LeftShift):
            self.DEBUG( "LeftShift" )
            expr = LeftShift((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.flatten_ast_add_assign( expr )
            return Name(new_varname)

        elif isinstance(node, RightShift):
            self.DEBUG( "RightShift" )
            expr = RightShift((self.flatten_ast(node.left), self.flatten_ast(node.right)))
            new_varname = self.flatten_ast_add_assign( expr )
            return Name(new_varname)

        elif isinstance( node, Bitand ):
            self.DEBUG( "Bitand" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = Bitand(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = Bitand([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return Name(new_varname)

        elif isinstance( node, Bitor ):
            self.DEBUG( "Bitor" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = Bitor(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = Bitor([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return Name(new_varname)

        elif isinstance( node, Bitxor ):
            self.DEBUG( "Bitxor" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = Bitxor(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = Bitxor([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return Name(new_varname)

        elif isinstance (node, Invert ):
            self.DEBUG("Invert")
            expr = Invert(self.flatten_ast(node.expr))
            new_varname = self.flatten_ast_add_assign(expr)    
            return Name(new_varname)

        ## probably not used anymore because of handeling in ast_insert
        elif isinstance( node, And ):
            self.DEBUG( "And" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = And(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = And([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return Name(new_varname)

        ## probably not used anymore because of handeling in ast_insert
        elif isinstance( node, Or ):
            self.DEBUG( "Or" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = Or(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr )
                elif (cnt > 1):
                    expr = Or([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr )
                cnt += 1
            return Name(new_varname)

        elif isinstance( node, Not ):
            self.DEBUG( "Not" )
            expr = Not(self.flatten_ast(node.expr))
            new_varname = self.flatten_ast_add_assign( expr )
            return Name(new_varname)

        elif isinstance( node, Compare ):
            self.DEBUG( "Compare" )
            cnt = 0
            for op in node.ops:
                flat_op = self.flatten_ast(op[1])
                if cnt == 0:
                    expr = Compare( self.flatten_ast( node.expr ), [(op[0], flat_op)] )
                else:
                    expr = Compare( Name( new_varname ), [(op[0], flat_op)] )
                new_varname = self.flatten_ast_add_assign_bool( expr, op[0] )
                cnt += 1
            return Name( new_varname )

        elif isinstance( node, If ):
            self.DEBUG( "If" )
            ## set end_label
            if flat_tmp != None:
                end_label = flat_tmp
            else:
                self.label_counter += 1
                end_label = self.templabel + str(self.label_counter)
            if len(node.tests) == 0:
                ## recursivity reached end
                if node.else_ is not None:
                    self.flatten_ast( node.else_ )
                    ## end_label
                    self.flat_ast.append( Label( LabelName( end_label ) ) )
            else:
                test1 = node.tests[0]
                ## set false_label
                if node.else_ is None  and len(node.tests) == 1:
                    false_label = end_label
                else:
                    self.label_counter += 1
                    false_label = self.templabel + str(self.label_counter)
                ## if not cond1 goto false_label
                new_varname = self.flatten_ast( Not( test1[0] ) )
                self.flat_ast.append( If( [( new_varname, LabelName( false_label ) )], None ) )
                ## statement1 (cond1 is True)
                self.flatten_ast( test1[1] )
                if node.else_ is not None or len(node.tests) > 1:
                    ## goto end_label
                    self.flat_ast.append( Goto( LabelName( end_label ) ) )
                ## start false_label and recoursively flatten If with one test less
                self.flat_ast.append( Label( LabelName( false_label ) ) )
                self.flatten_ast( If( node.tests[1:], node.else_ ), end_label )
            return

        elif isinstance( node, While ):
            self.DEBUG( "While" )
            ## create labels
            self.label_counter += 1
            top_label = self.templabel + str(self.label_counter)
            self.label_counter += 1
            test_label = self.templabel + str(self.label_counter)
            ## goto test
            self.flat_ast.append( Goto( LabelName( test_label ) ) )
            ## topLabel:
            self.flat_ast.append( Label( LabelName( top_label ) ) )
            ## flatten while body
            self.flatten_ast( node.body )
            ## testLabel:
            self.flat_ast.append( Label( LabelName( test_label ) ) )
            ## flatten condition
            new_varname = self.flatten_ast( node.test )
            ## test
            self.flat_ast.append( If( [( new_varname, LabelName( top_label ) )], None ) )
            return

        else:
            die( "unknown AST node" + str( node ) )

    ## helper for flatten_ast
    def flatten_ast_add_assign( self, expr ):
        self.var_counter += 1
        name = self.tempvar + str( self.var_counter )
        nodes = AssName(name, 'OP_ASSIGN')
        self.flat_ast.append( Assign( [nodes], expr ) )
        self.DEBUG( "\t\t\tnew statement node: append Assign" + str( name ) )
        return name

    def flatten_ast_add_assign_bool( self, expr, op ):
        self.var_counter += 1
        name = self.tempvar + str( self.var_counter )
        nodes = AssName( name, 'OP_ASSIGN' )
        self.flat_ast.append( AssignBool( [nodes], expr, op ) )
        self.DEBUG( "\t\t\tnew statement node: append AssignBool" + str( name ) )
        return name


    ## convert the flattened AST into a list of ASM expressions
    ###########################################################
    def flatten_ast_2_list( self, nd ):
        if isinstance( nd, Module ):
            self.DEBUG( "Module" )
            self.flatten_ast_2_list( nd.node )
            return self.expr_list

        elif isinstance( nd, Stmt ):
            self.DEBUG( "Stmt" )
            ## program
            for chld in nd.getChildren():
                self.flatten_ast_2_list( chld )
            return

        elif isinstance( nd, Add ):
            self.DEBUG( "Add" )
            left = self.vartable_lookup( nd.left.name )
            right = self.vartable_lookup( nd.right.name )
            ret = left
            self.expr_list.append( ASM_addl( right, ret ) )
            return ret

        elif isinstance( nd, Sub ):
            self.DEBUG( "Sub" )
            left = self.vartable_lookup( nd.left.name )
            right = self.vartable_lookup( nd.right.name )
            ret = left
            self.expr_list.append( ASM_subl( right, ret ) )
            return ret

        elif isinstance( nd, Mul ):
            self.DEBUG( "Mul" )
            left = self.vartable_lookup( nd.left.name )
            right = self.vartable_lookup( nd.right.name )
            ret = left
            self.expr_list.append( ASM_imull( right, ret ) )
            return ret

        elif isinstance( nd, Bitand ):
            self.DEBUG( "Bitand" )
            left = self.vartable_lookup( nd.nodes[0].name )
            right = self.vartable_lookup( nd.nodes[1].name )
            ret = left
            self.expr_list.append( ASM_andl( right, ret ) )
            return ret

        elif isinstance( nd, Bitor ):
            self.DEBUG( "Bitor" )
            left = self.vartable_lookup( nd.nodes[0].name )
            right = self.vartable_lookup( nd.nodes[1].name )
            ret = left
            self.expr_list.append( ASM_orl( right, ret ) )
            return ret

        elif isinstance( nd, Bitxor ):
            self.DEBUG( "Bitxor" )
            left = self.vartable_lookup( nd.nodes[0].name )
            right = self.vartable_lookup( nd.nodes[1].name )
            ret = left
            self.expr_list.append( ASM_xorl( right, ret ) )
            return ret

        elif isinstance( nd, Invert ):
            self.DEBUG( "Invert" )
            op = self.vartable_lookup(nd.expr.name)
            ret = op
            self.expr_list.append( ASM_notl( ret ) )
            return ret

        elif isinstance( nd, UnarySub ):
            self.DEBUG( "UnarySub" )
            op = self.vartable_lookup(nd.expr.name)
            ret = op
            self.expr_list.append( ASM_negl( ret ) )
            return ret

        elif isinstance( nd, LeftShift ):
            self.DEBUG( "LeftShift" )
            left = self.vartable_lookup( nd.left.name )
            right = self.vartable_lookup( nd.right.name )
            ## shift needs the shifting value in the register ecx
            ## and is called with %cl
            self.expr_list.append( ASM_movl( right, self.reg_list['ecx'] ) )
            ret = left
            self.expr_list.append( ASM_shll( ASM_register('cl'), ret ) )
            return ret

        elif isinstance( nd, RightShift ):
            self.DEBUG( "LeftRight" )
            left = self.vartable_lookup( nd.left.name )
            right = self.vartable_lookup( nd.right.name )
            ## shift needs the shifting value in the register ecx
            ## and is called with %cl
            self.expr_list.append( ASM_movl( right, self.reg_list['ecx'] ) )
            ret = left
            self.expr_list.append( ASM_shrl( ASM_register('cl'), ret ) )
            return ret

        elif isinstance( nd, Assign ) or isinstance( nd, AssignBool ):
            nam = nd.nodes[0].name ## just consider the first assignement variable
            new_def_elem = self.vartable_lookup( nam, False )
            op = self.flatten_ast_2_list( nd.expr )
            if isinstance( nd, Assign ):
                self.DEBUG( "Assign" )
                self.expr_list.append( ASM_movl( op, new_def_elem ) )
            elif isinstance( nd, AssignBool ):
                self.DEBUG( "AssignBool" )
                ## move condition flag (former operation must be ASM_cond() ) into new_def_elem
                if nd.comp == '<':
                    self.expr_list.append( ASM_setlb( new_def_elem ) )
                elif nd.comp == '<=':
                    self.expr_list.append( ASM_setleb( new_def_elem ) )
                elif nd.comp == '>':
                    self.expr_list.append( ASM_setgb( new_def_elem ) )
                elif nd.comp == '>=':
                    self.expr_list.append( ASM_setgeb( new_def_elem ) )
                elif nd.comp == '==':
                    self.expr_list.append( ASM_seteb( new_def_elem ) )
                elif nd.comp == '!=':
                    self.expr_list.append( ASM_setneb( new_def_elem ) )
                else:
                    die( "ERROR: unknown compare operator" )

            if isinstance( new_def_elem, ASM_v_register ) and new_def_elem.is_new():
                ## new_def_elem was priviously spilled and needs to be moved to the stack
                self.expr_list.append( ASM_movl( new_def_elem, self.stack_lookup( new_def_elem.get_name(), False ) ) )
                new_def_elem.set_new( False )
            return

        elif isinstance( nd, CallFunc ):
            self.DEBUG( "CallFunc" )
            ## lhs is name of the function
            ## rhs is name of the temp var for the param tree
            stack_offset = 0
            for attr in reversed(nd.args):
                self.expr_list.append(
                    ASM_movl( self.flatten_ast_2_list( attr ), ASM_stack( stack_offset, self.reg_list['esp']) )
                )
                stack_offset += 4
            myCallObj = ASM_call( nd.node.name )
            myCallObj.set_r_def( self.reg_list['eax'] )
            myCallObj.set_r_ignore( self.reg_list['eax'] )
            myCallObj.set_r_ignore( self.reg_list['ecx'] )
            myCallObj.set_r_ignore( self.reg_list['edx'] )
            self.expr_list.append( myCallObj )
            return self.reg_list['eax']

        elif isinstance( nd, Discard ):
            self.DEBUG( "Discard" )
            ## discard all below
            return

        elif isinstance( nd, Name ):
            self.DEBUG( "Name" )
            return self.vartable_lookup( nd.name )

        elif isinstance( nd, LabelName ):
            self.DEBUG( "LabelName" )
            return self.labeltable_lookup( nd.name )
 
        elif isinstance( nd, Const ):
            self.DEBUG( "Const" )
            return ASM_immedeate(nd.value)

        elif isinstance( nd, AssName ):
            ## handled by higher node
            self.DEBUG( "AssName" )
            return

        elif isinstance( nd, Compare ):
            self.DEBUG( "Compare" )
            op1 = nd.ops[0]
            self.expr_list.append(
                ASM_cmpl( self.flatten_ast_2_list( nd.expr ), self.flatten_ast_2_list( op1[1] ) )
            )
            ## no return value needed, this is handeled in AssignBool
            return

        elif isinstance( nd, Not ):
            self.DEBUG( "Not" )
            v_reg = self.flatten_ast_2_list( nd.expr )
            self.expr_list.append( ASM_notl( v_reg ) )
            return v_reg

        elif isinstance( nd, If ):
            self.DEBUG( "If" )
            ## check if nd.tests[0][0] is true
            self.expr_list.append( ASM_cmpl( ASM_immedeate( 0 ), self.flatten_ast_2_list( nd.tests[0][0] ) ) )
            self.expr_list.append( ASM_je( self.flatten_ast_2_list( nd.tests[0][1] ) ) )
            return

        elif isinstance( nd, Goto ):
            self.DEBUG( "Goto" )
            self.expr_list.append( ASM_jmp( self.flatten_ast_2_list( nd.label ) ) )
            return

        elif isinstance( nd, Label ):
            self.DEBUG( "Label" )
            self.expr_list.append( ASM_plabel( self.flatten_ast_2_list( nd.name ) ) )
            return

        else:
            self.DEBUG( "*** ELSE ***" )
            return

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

    def get_prolog( self ):
        prolog = []
        ## asm prolog
        prolog.append( ASM_text("text") )
        prolog.append( ASM_plabel( self.labeltable_lookup( "LC0" ) ) )
        prolog.append( ASM_text("ascii \"Compiled with JPSM!\"") )
        prolog.append( ASM_text("globl main") )
        prolog.append( ASM_plabel( self.labeltable_lookup( "main" ) ) )
        prolog.append( ASM_pushl( self.reg_list['ebp'] ) )
        prolog.append( ASM_movl( self.reg_list['esp'], self.reg_list['ebp'] ) )
        prolog.append( ASM_subl( ASM_immedeate( self.init_stack_mem(self.asmlist_mem) ), self.reg_list['esp'] ) )
        return prolog

    def get_epilog( self ):
        epilog = []
        epilog.append( ASM_movl( ASM_stack( 0, self.reg_list['ebp'] ), self.reg_list['eax'] ) )
        epilog.append( ASM_leave() )
        epilog.append( ASM_ret() )
        return epilog

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
            self.var_counter += 1
            new_name = self.tempvar + str(self.var_counter)
            new_elem = ASM_v_register( new_name ) ## new v_register
            self.asmlist_vartable.update({new_name:new_elem})
            self.expr_list.append( ASM_movl( stack_pos, new_elem ) )
            v_reg = new_elem
        elif v_reg.is_spilled() and not defined:
            ## instruction call defining the spilled v_reg
            self.var_counter += 1
            new_name = self.tempvar + str(self.var_counter)
            v_reg.set_spilled_name( new_name ) ## indicate to the old v_reg the name of the new v_reg
            new_elem = ASM_v_register( new_name )
            self.asmlist_vartable.update({new_name:new_elem})
            new_elem.set_new( True )
            v_reg = new_elem
        return v_reg

    def labeltable_lookup( self, nam ):
        if nam not in self.asmlist_labeltable:
            ## var is new -> add a new label object to the dict
            new_elem = ASM_label( nam )
            self.asmlist_labeltable.update({nam:new_elem})
        ## return labeltable object
        return self.asmlist_labeltable[nam]

    def cleanup_asm( self ):
        iter_list = self.expr_list
        self.expr_list = []
        for expr in iter_list:
            if isinstance(expr, ASM_movl):
                ## cleanup move expressions moving a register to itself
                left_color = None
                right_color = None
                if isinstance(expr.left, ASM_v_register):
                    left_color = expr.left.get_color()
                elif isinstance(expr.left, ASM_register):
                    left_color = expr.left
                if isinstance(expr.right, ASM_v_register):
                    right_color = expr.right.get_color()
                elif isinstance(expr.right, ASM_register):
                    right_color = expr.right
                if left_color == None or right_color == None or left_color != right_color:
                    self.expr_list.append(expr)
            else:
                self.expr_list.append(expr)


    ## liveness analysis
    ####################
#    def liveness( self ):
#        changed = True
#        live_in = [[]]
#        live_out = [[]]
#        while changed:
#            changed = False
#            (live_in, live_out) = self.liveness_bb( live_in, live_out )
#            for i in range(0, len(self.expr_list), 1):
#                if live_in[i] != live_out[i+1]:
#                    self.DEBUG( str(i) + " " + self.concat_live(live_in[i]) + " " + self.concat_live(live_out[i+1]) )
#                    changed = True
#        return live_out

    def liveness( self ):
        changed = True
        live_in = []
        live_in_old = []
        live_out = [[]]
        live_out_old = [[]]
        for i in range(0, len(self.expr_list), 1):
            live_in.append([])
            live_in_old.append([])
            live_out.append([])
            live_out_old.append([])
        while changed:
            changed = False
            j = 0
            last_ignores = []
            label_list = {}
            remove_ignores = False
            for i in range( len(self.expr_list), 0, -1 ):
                element = self.expr_list[i-1]
                ## LIVE_in(i) = ( LIVE_out(i) - DEF(i) ) union USE(i)
                temp_live = self.sub_def_live( element.get_r_def(), list(live_out[j]), live_out[j] )
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
                if isinstance(element, ASM_plabel):
                    ## get all labels from asm list (possible succeeders)
                    label_list.update({element.label:temp_live})
                live_in_old[j] = live_in[j]
                live_in[j] = temp_live
                ## LIVE_out(i) = union_{j in succ(i)} LIVE_in(j)
                if isinstance( element, ASM_jmp ):
                    if element.label not in label_list:
                        label_list.update({element.label:[]})
                    succ_union = label_list[element.label] 
                elif isinstance( element, ASM_je ):
                    if element.label not in label_list:
                        label_list.update({element.label:[]})
                    succ_union = self.add_use_live( label_list[element.label], temp_live )
                else:
                    succ_union = temp_live
                live_out_old[j+1] = live_out[j+1]
                live_out[j+1] = succ_union
                if self.concat_live(live_out_old[j+1]) != self.concat_live(live_out[j+1]) or self.concat_live(live_in_old[j]) != self.concat_live(live_in[j]):
                    changed = True
                j += 1
        return live_out

    ## helper for liveness   
    def sub_def_live( self, defi, live, live_ptr=None ):
        is_live = False
        for oper1 in defi:
            for oper2 in live:
                if oper1.get_content().get_name() == oper2.get_content().get_name():
                    live.remove( oper2 )
                    is_live = True
            if not is_live and live_ptr != None:
                ## the variable was defined but never used
                ## -> add edges in ig with all live vars just before the def
                oper1.set_ignore( True )
                live_ptr.append( oper1 )
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
                    if isinstance( reg, ASM_register ):
                        node = Node( reg, reg, False )
                    else:
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
            picked = True
        if not picked:
            ## picked_node contains a v_register
            for reg_name in self.reg_list:
                color = self.reg_list[reg_name]
                if color.is_caller():
                    pick = True
                    ## check if another node with the same color is connected
                    for connected_node in ig.get_connected_nodes( picked_node ):
                        if connected_node.is_active() and color == connected_node.get_color():
                            pick = False
                            break
                    if pick:
                        ## no other node with the same color is connected
                        picked_node.set_color(color)
                        picked = True
                        break
        if not picked:
            ## spill this node
            self.DEBUG( "Spilled " + str(picked_node) )
            picked_node.get_content().set_spilled( True )
            return False
        return ig

    ## print
    ########
    def print_asm( self, expr_lst, alloc=False ):
        self.DEBUG('\n\n\n')
        for expr in expr_lst:
            if alloc:
                print expr.print_alloc()
            else:
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
    CLEANUP_ASM = False
    PRINT_PSEUDO = False
    GEN_PSEUDO = False
    PRINT_LIVENESS = False
    GEN_LIVENESS = False
    PRINT_IG = False
    GEN_IG = False
    PRINT_IG_COLOR = False
    GEN_IG_COLOR = False
    PRINT_ALLOC = False
    GEN_ALLOC = False
    if "-help" in sys.argv:
        usage()
        sys.exit( 0 ) 
    if 1 < len( sys.argv[1:] ) and "-debug" in sys.argv:
        DEBUG = True
    if 1 < len( sys.argv[1:] ) and "-o" in sys.argv:
        CLEANUP_ASM = True
    if 1 < len( sys.argv[1:] ) and "-pseudo" in sys.argv:
        GEN_PSEUDO = True
        PRINT_PSEUDO = True
    elif 1 < len( sys.argv[1:] ) and "-liveness" in sys.argv:
        GEN_PSEUDO = True
        GEN_LIVENESS = True
        PRINT_LIVENESS = True
    elif 1 < len( sys.argv[1:] ) and "-ig" in sys.argv:
        GEN_PSEUDO = True
        GEN_LIVENESS = True
        GEN_IG = True
        PRINT_IG = True
    elif 1 < len( sys.argv[1:] ) and "-ig-color" in sys.argv:
        GEN_PSEUDO = True
        GEN_LIVENESS = True
        GEN_IG = True
        GEN_IG_COLOR = True
        PRINT_IG_COLOR = True
    elif 1 < len( sys.argv[1:] ) and "-alloc" in sys.argv:
        GEN_PSEUDO = True
        GEN_LIVENESS = True
        GEN_IG = True
        GEN_IG_COLOR = True
        GEN_ALLOC = True
        PRINT_ALLOC = True
    else:
        ## use alloc as default
        GEN_PSEUDO = True
        GEN_LIVENESS = True
        GEN_IG = True
        GEN_IG_COLOR = True
        GEN_ALLOC = True
        PRINT_ALLOC = True

    ## generate assembler
    compl = Engine( sys.argv[-1], DEBUG )
    compl.compileme()

    ## perform liveness/coloring/spilling and generate ig
    liveness = None
    ig = None
    ig_color = None
    if GEN_IG_COLOR:
        ig_color = False
        while True:
            compl.compileme( None, False )
            liveness = compl.liveness()
            ig = compl.create_ig( liveness )
            ig_color = compl.color_ig( ig )
            if ig_color != False:
                break
    elif GEN_IG:
        ig = compl.create_ig( compl.liveness() )
    elif GEN_LIVENESS:
        liveness = compl.liveness()

    if CLEANUP_ASM:
        compl.cleanup_asm()

    ## print results
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

        print "len of asmlist_labeltable '%d'" % len(compl.asmlist_labeltable)
        print compl.asmlist_labeltable

        print "len of asmlist_stack '%d'" % len(compl.asmlist_stack)
        print compl.asmlist_stack

        print "asmlist_mem '%d'" % compl.asmlist_mem

    if PRINT_IG:
        compl.print_ig( ig )
    elif PRINT_IG_COLOR:
        compl.print_ig( ig_color )
    elif PRINT_LIVENESS:
        compl.print_liveness( liveness )
    elif PRINT_PSEUDO:
        compl.print_asm( compl.expr_list )
    elif PRINT_ALLOC:
        ## object that call the method, print_asm, with the argument compl.expr_list OF THE CLASS ENGINE
        compl.print_asm( compl.get_prolog() ) 
        compl.print_asm( compl.expr_list, True )
        compl.print_asm( compl.get_epilog() )
    else:
        usage()
        die( "ERROR: wrong parametrisation" ) 

else:        
    usage()
