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
from pp import *

## auxiliary
def die( meng ):
    print meng
    sys.exit( -1 )

def usage():
    print "USAGE:"
    print "    %s [OPERATION] [ARGUMENT] FILE" % sys.argv[0]
    print "OPERATION:"
    print "    -pseudo:   prints ASM-pseudo-code using virtual registers"
#    print "    -liveness: prints the liveness analysis of the -pseudo ASM"
#    print "    -ig:       prints dot syntax of the interference graph"
#    print "    -ig-color: prints dot syntax of the colored interference graph"
#    print "    -alloc:    prints ASM-code using register allocation (default)"
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

class Pointer(Node):
    def __init__(self, name):
        self.name = name

    def getChildren(self):
        return (self.name)

    def getChildNodes(self):
        return (self.name)


## P0 compiler implementation
#############################
class Engine( object ):
    def __init__( self, filepath=None, DEBUG=False, STACK=False ):
        self.DEBUGMODE = DEBUG
        self.STACK = STACK
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
        self.cond_label_cnt = 0
        self.cond_label = "L"
        self.str_label_cnt = 0
        self.str_label = ".LC"
        self.meth_label_cnt = 0
        self.meth_label = "Cm"
        #self.box_int = "create_int"
        #self.box_bool = "create_bool"
        #self.box_big = "create_big"
        self.box_int = "inject_int"
        self.box_bool = "inject_bool"
        self.box_big = "inject_big"
        self.unbox_int = "project_int"
        self.unbox_bool = "project_bool"
        self.unbox_big = "project_big"

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
#            'ax':ASM_register('ax'),
#            'ah':ASM_register('ah'),
#            'al':ASM_register('al'),
#            'bx':ASM_register('bx'),
#            'bh':ASM_register('bh'),
#            'bl':ASM_register('bl'),
#            'cx':ASM_register('cx'),
#            'ch':ASM_register('ch'),
#            'cl':ASM_register('cl'),
#            'dx':ASM_register('dx'),
#            'dh':ASM_register('dh'),
#            'dl':ASM_register('dl'),
        }
        ## list handling
        self.init_class = '$_object'
        self.asmlist_labeltable = {}
        self.scope = {
            'main':{
                'vartable':{},
                'stack':{},
                'asm_list':[],
                'stack_cnt':0,
            }
        }
        self.class_ref = {
            self.init_class:{
                'class_ptr':None,
                'object_list':{},   ## obj_name:{'obj_ptr':obj_ptr, 'class_name':class_name}
                'string_list':{},   ## {meth/attr}_name:ASM_str_label -> $.LC0
                'super_class':None
            }
        }
        self.scope_list = ['main']
        self.scope_cnt = 0

    def compileme( self, compute_ast=True ):
       # for block in self.scope:
       #     self.scope[block]['vartable'] = {}
       #     self.scope[block]['stack'] = {}
       #     self.scope[block]['asm_list'] = []
       #     self.scope[block]['stack_cnt'] = 0
        if compute_ast:
            if DEBUG: self.DEBUG__print_ast( self.ast )

            self.DEBUG( "\nCOMPUTE INSERT_AST" )
            self.scope_cnt = 0
            insert_ast = self.insert_ast(self.ast, [], self.class_ref[self.init_class])
            if DEBUG: self.DEBUG__print_insert_ast( insert_ast )

            self.DEBUG( "\nCOMPUTE FLATTEN_AST" )
            self.scope_cnt = 0
            self.flat_ast = self.flatten_ast( insert_ast, [], None )
            if DEBUG: self.DEBUG__print_flatten_ast( self.flat_ast )

        self.DEBUG( "\nCOMPUTE AST_2_ASM" )
        self.scope_cnt = 0
        self.flatten_ast_2_list( self.flat_ast, None )
        self.DEBUG( "\n=====================================================\n" )

    def check_plain_integer( self, val ):
        if isinstance( val, LabelName ):
            return val
        elif type( val ) is not int:
            die( "ERROR: syntax error, no plain integer allowed, val: " + str(val) )
        return val

    def insert_ast( self, node, parent_stmt, class_ref, temp=None ):
        if isinstance( node, Module ):
            self.DEBUG( "Module_insert" )
            ## don't ask why -> need to check
            ## if there is no "normal" variable assigned in the code, it may happen that
            ## wrong parameters are passed to a function
            self.var_counter += 1
            new_varname = self.tempvar + str( self.var_counter )
            node.node.nodes.insert(0, Assign( [AssName( new_varname, 'OP_ASSIGN' )], Const(0) ))
            insertar = Module( None, self.insert_ast(node.node, parent_stmt, class_ref ) )
            return insertar

        elif isinstance( node, Stmt ):
            self.DEBUG( "Stmt_insert" )
            chain = []
            for n in node.nodes:
                elem = self.insert_ast( n, chain, class_ref )
                if elem != None:
                    chain.append( elem )
            return Stmt( chain )

        elif isinstance( node, Const ):
            self.DEBUG( "Const_insert" )
            return CallFunc( Name( self.box_int ), [Const( node.value )] )

        elif isinstance( node, Name ):
            self.DEBUG( "Name_insert" )
            if node.name == 'True':
                expr = CallFunc( Name( self.box_bool ), [Const( 1 )] )
            elif node.name == 'False':
                expr = CallFunc( Name( self.box_bool ), [Const( 0 )] )
            elif node.name == 'None':
                expr = CallFunc( Name( self.box_big ), [Const( 0 )] )
            else:
                expr = node
            return expr

        elif isinstance( node, Add ):
            self.DEBUG( "Add_insert" )
            left = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.left, parent_stmt, class_ref )] )
            right = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.right, parent_stmt, class_ref )] )
            return CallFunc( Name( self.box_int ), [Add( (left, right) )] )

        elif isinstance( node, Sub ):
            self.DEBUG("Sub_insert")
            left = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.left, parent_stmt, class_ref )] )
            right = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.right, parent_stmt, class_ref )] )
            return CallFunc( Name( self.box_int ), [Sub( (left, right) )] )

        elif isinstance( node, Mul ):
            self.DEBUG( "Mul_insert" )
            left = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.left, parent_stmt, class_ref )] )
            right = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.right, parent_stmt, class_ref )] )
            return CallFunc( Name( self.box_int ), [Mul( (left, right) )] )

        elif isinstance( node, UnarySub ):
            self.DEBUG( "UnarySub_insert" )
            expr = self.insert_ast( node.expr, parent_stmt, class_ref )
            return CallFunc( Name( self.box_int ), [UnarySub( CallFunc( Name( self.unbox_int ), [expr] ) )] )

        elif isinstance( node, UnaryAdd ):
            self.DEBUG( "UnaryAdd_insert" )
            ## ignore UnaryAdd node and use only its content
            expr = self.insert_ast( node.expr, parent_stmt, class_ref )
            return CallFunc( Name( self.box_int ), [UnaryAdd( CallFunc( Name( self.unbox_int ), [expr] ) )] )

        elif isinstance( node, Invert ):
            self.DEBUG( "Invert_insert" )
            expr = self.insert_ast( node.expr, parent_stmt, class_ref )
            return CallFunc( Name( self.box_int ), [Invert( CallFunc( Name( self.unbox_int ), [expr] ) )] )

        elif isinstance( node, LeftShift ):
            self.DEBUG( "LeftShift_insert" )
            left = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.left, parent_stmt, class_ref )] )
            right = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.right, parent_stmt, class_ref )] )
            return CallFunc( Name( self.box_int ), [LeftShift( (left, right) )] )

        elif isinstance( node, RightShift ):
            self.DEBUG( "RightShift_insert" )
            left = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.left, parent_stmt, class_ref )] )
            right = CallFunc( Name( self.unbox_int ), [self.insert_ast( node.right, parent_stmt, class_ref )] )
            return CallFunc( Name( self.box_int ), [RightShift( (left, right) )] )

        elif isinstance( node, Discard ):
            self.DEBUG( "Discard_insert" )
            expr = self.insert_ast( node.expr, parent_stmt, class_ref )
            return Discard( expr )

        elif isinstance( node, AssName ):
            self.DEBUG( "AssName_insert" )
            return node

        elif isinstance( node, Assign ):
            self.DEBUG( "Assign_insert" )
            if isinstance ( node.nodes[0], AssAttr ):
                ## addressing an attribute in an object
                attrname = node.nodes[0].attrname
                ## special case: pass the assign name to the next step (object creation)
                expr = self.insert_ast( node.expr, parent_stmt, class_ref, attrname )
                obj_ptr = self.lookup_object_ptr( node.nodes[0].expr.name, class_ref )
                if attrname not in class_ref['string_list']:
                    new_str_label = self.str_label + str( self.str_label_cnt )
                    self.str_label_cnt += 1
                    class_ref['string_list'].update( {attrname:new_str_label} )
                else:
                    new_str_label = self.lookup_string( attrname, class_ref )
                self.var_counter += 1
                new_varname = self.tempvar + str( self.var_counter )
                ret = CallFunc( Name( 'set_attr' ), [obj_ptr, Const( LabelName( new_str_label ) ), expr] )
                ret = Assign( [AssName( new_varname, 'OP_ASSIGN' )], ret )
            elif isinstance( node.nodes[0], AssName ):
                ## special case: pass the assign name to the next step (object creation)
                expr = self.insert_ast( node.expr, parent_stmt, class_ref, node.nodes[0].name )
                ret = Assign( [node.nodes[0]], expr )
            else:
                nodes = self.insert_ast( node.nodes[0], parent_stmt, class_ref )
                expr = self.insert_ast( node.expr, parent_stmt, class_ref )
                ret = Assign( [nodes], expr )
            return ret

        elif isinstance( node, Bitand ):
            self.DEBUG( "Bitand_insert" )
            chain = []
            for attr in node.nodes:
                chain.append( CallFunc( Name( self.unbox_int ), [self.insert_ast( attr, parent_stmt, class_ref )] ) )
            return CallFunc( Name( self.box_int ), [Bitand( chain )] )

        elif isinstance( node, Bitor ):
            self.DEBUG( "Bitor_insert" )
            chain = []
            for attr in node.nodes:
                chain.append( CallFunc( Name( self.unbox_int ), [self.insert_ast( attr, parent_stmt, class_ref )] ) )
            return CallFunc( Name( self.box_int ), [Bitor( chain )] )

        elif isinstance( node, Bitxor ):
            self.DEBUG( "Bitxor_insert" )
            chain = []
            for attr in node.nodes:
                chain.append( CallFunc( Name( self.unbox_int ), [self.insert_ast( attr, parent_stmt, class_ref )] ) )
            return CallFunc( Name( self.box_int ), [Bitxor( chain )] )

        elif isinstance(node, And):
            self.DEBUG( "And_insert" )
            ## special case: don't box and unbox here -> is handeled in flatten_ast
            chain = []
            for attr in node.nodes:
                chain.append( self.insert_ast( attr, parent_stmt, class_ref ) )
            return And( chain )

        elif isinstance( node, Not ):
            self.DEBUG( "Not_insert" )
            expr = self.insert_ast( node.expr, parent_stmt, class_ref )
            return CallFunc( Name( self.box_bool ), [Not( CallFunc( Name( self.unbox_bool ), [expr] ) )] )

        elif isinstance( node, Or ):
            self.DEBUG( "Or_insert" )
            ## special case: don't box and unbox here -> is handeled in flatten_ast
            chain = []
            for attr in node.nodes:
                chain.append( self.insert_ast( attr, parent_stmt, class_ref ) )
            return Or( chain )

        elif isinstance( node, Compare ):
            self.DEBUG( "Compare_insert" )
            expr = self.insert_ast( node.expr, parent_stmt, class_ref )
            chain_final = []
            for attr in node.ops:
                if attr[0] == '==':
                    operand_2 = self.insert_ast( attr[1], parent_stmt, class_ref )
                    return CallFunc( Name( self.box_bool ), [CallFunc( Name( 'equal' ), [expr, operand_2] )])
                elif attr[0] == '!=':
                    operand_2 = self.insert_ast( attr[1], parent_stmt, class_ref )
                    return CallFunc( Name( self.box_bool ), [Not( CallFunc( Name( 'equal' ), [expr, operand_2] ) )] )
                elif node.expr != True and node.expr != False:
                    operand_1 = attr[0]
                    operand_2 = self.insert_ast( attr[1], parent_stmt, class_ref )
                    chain_final.append( (operand_1, CallFunc( Name( self.unbox_int ), [operand_2] )) )
                    expr = Compare( CallFunc( Name( self.unbox_int ), [expr] ),chain_final )
                    return CallFunc( Name( self.box_bool ), [expr] )
                else:
                    operand_1 = attr[0]
                    operand_2 = self.insert_ast( attr[1], parent_stmt, class_ref )
                    chain_final.append( (operand_1, CallFunc( Name( self.unbox_bool ), [operand_2] )) )
                    expr = Compare( CallFunc( Name( self.unbox_bool ), [expr] ),chain_final )
                    return CallFunc( Name( self.box_bool ), [expr] )

        elif isinstance( node, If ):
            self.DEBUG( "If_insert" )
            chain = []
            for attr in node.tests:
                left = self.insert_ast( attr[0], parent_stmt, class_ref )
                right = self.insert_ast( attr[1], parent_stmt, class_ref )
                chain.append( (CallFunc( Name( self.unbox_bool ), [left]), right) )
            other = None
            if node.else_ != None:
                other = self.insert_ast( node.else_, parent_stmt, class_ref )
            return If( chain, other )

        elif isinstance( node, While ):
            self.DEBUG( "While_insert" )
            chain = []
            test = CallFunc( Name( self.unbox_bool ), [self.insert_ast( node.test, parent_stmt, class_ref )] )
            body = self.insert_ast( node.body, parent_stmt, class_ref )
            other = None
            if node.else_ != None:
                other = self.insert_ast( node.else_, parent_stmt, class_ref )
            return While( test, body, other )

        elif isinstance( node, Printnl ):
            self.DEBUG( "Printnl_insert" )
            chain = []
            for attr in node.nodes:
                chain.append( self.insert_ast( attr, parent_stmt, class_ref ) )
            return Printnl( chain, None )

        elif isinstance( node, Print ):
            self.DEBUG( "Print_insert" )
            chain = []
            for attr in node.nodes:
                chain.append( self.insert_ast( attr, parent_stmt, class_ref ) )
            return Print( chain, None )

        elif isinstance( node, CallFunc ):
            self.DEBUG( "CallFunc_insert" )
            if isinstance( node.node, Getattr ):
                ## call of a method
                obj_name = node.node.expr.name
                meth_name = node.node.attrname
                temp_class_ref = class_ref
                if obj_name != 'self':
                    ## set reference to corresponding class
                    class_name = self.lookup_object_class_name( obj_name, class_ref )
                    temp_class_ref = self.class_ref[class_name]
                ## get method label from class
                meth_label = self.lookup_string( meth_name, temp_class_ref )
                ## get object pointer from object
                obj_ptr = self.lookup_object_ptr( obj_name, class_ref )
                label_name = Const( LabelName( meth_label ) )
                fun_ptr = CallFunc( Name( 'get_fun_ptr_from_attr' ), [obj_ptr, label_name] )
                self.var_counter += 1
                new_fun_varname = self.tempvar + str( self.var_counter )
                parent_stmt.append( Assign( [AssName( new_fun_varname, 'OP_ASSIGN' )], fun_ptr ) )
                ## handle arguments
                args = []
                for arg in node.args:
                    if arg in class_ref['object_list']:
                        ## FIXME: passing objects as parameter is not working
                        ## update class_ref of owner of function
                        pass
                    args.append( self.insert_ast( arg, parent_stmt, class_ref ) )
                args.insert( 0, obj_ptr )
                return CallFunc( Pointer( new_fun_varname ), args )
            else:
                if node.node.name in self.class_ref:
                    ## object allocation
                    class_name = node.node.name
                    class_ptr = self.class_ref[class_name]['class_ptr']
                    obj_ptr = CallFunc( Name( 'create_object' ), [class_ptr] )
                    self.var_counter += 1
                    new_varname = self.tempvar + str( self.var_counter )
                    parent_stmt.append( Assign( [AssName( new_varname, 'OP_ASSIGN' )], obj_ptr ) )
                    obj_name_ptr = Name( new_varname )
                    class_ref['object_list'].update({
                        temp:{
                            'obj_ptr':obj_name_ptr,
                            'class_name':class_name
                        }
                    })
                    attrname = self.lookup_string( '__init__', self.class_ref[class_name] )
                    label_name = Const( LabelName( attrname ) )
                    fun_ptr = CallFunc( Name( 'get_fun_ptr_from_attr' ), [obj_name_ptr, label_name] )
                    self.var_counter += 1
                    new_varname = self.tempvar + str( self.var_counter )
                    parent_stmt.append( Assign( [AssName( new_varname, 'OP_ASSIGN' )], fun_ptr ) )
                    ## handle arguments
                    args = []
                    for arg in node.args:
                        if arg in class_ref['object_list']:
                            ## FIXME: passing objects as parameter is not working
                            ## update class_ref of owner of function
                            pass    
                        args.append( self.insert_ast( arg, parent_stmt, class_ref ) )
                    args.insert( 0, obj_name_ptr )
                    return CallFunc( Pointer( new_varname ), args )
                else:
                    ## normal function call
                    chain = []
                    for arg in node.args:
                        chain.append( self.insert_ast( arg, parent_stmt, class_ref ) )
                    return CallFunc( self.insert_ast( node.node, parent_stmt, class_ref ), chain )

        elif isinstance( node, Getattr ):
            self.DEBUG( "Getatrr_insert" )
            obj_name = node.expr.name
            obj_ptr = self.lookup_object_ptr( obj_name, class_ref )
            temp_class_ref = class_ref
            if obj_name != 'self':
                ## set reference to corresponding class
                class_name = self.lookup_object_class_name( obj_name, class_ref )
                temp_class_ref = self.class_ref[class_name]
            attrname = self.lookup_string( node.attrname, temp_class_ref )
            return CallFunc( Name( 'get_attr' ), [obj_ptr, Const( LabelName( attrname ) )] )

        elif isinstance( node, Class ):
            self.DEBUG( "Class_insert" )
            ## handle parent class
            zero = self.insert_ast( Const( 0 ), parent_stmt, class_ref )
            one = self.insert_ast( Const( 1 ), parent_stmt, class_ref )
            super_name = None
            if len(node.bases) > 0:
                super_name = node.bases[0].name
                self.var_counter += 1
                if super_name == "object":
                    if super_name not in self.class_ref:
                        base = CallFunc( Name( 'create_list' ), [zero] )
                        class_ptr = CallFunc( Name( 'create_class' ), [base] )
                        parent_stmt.append( Assign( [AssName( LabelName( super_name ), 'OP_ASSIGN' )], class_ptr ) )
                        self.class_ref.update({
                            super_name:{
                                'class_ptr':LabelName( super_name ),
                                'object_list':{},
                                'string_list':{},
                                'super_class':None
                            }
                        })
                new_varname = self.tempvar + str( self.var_counter )
                list1 = CallFunc( Name( 'create_list' ), [one] )
                base = Name( new_varname )
                parent_stmt.append( Assign( [AssName( new_varname, 'OP_ASSIGN')], list1 ) )
                parent_stmt.append( CallFunc( Name( 'set_subscript' ), [base, zero, LabelName( super_name )] ) )
            else:
                base = CallFunc( Name( 'create_list' ), [zero] )
            class_ptr = CallFunc( Name( 'create_class' ), [base] )
            parent_stmt.append( Assign( [AssName( LabelName( node.name ), 'OP_ASSIGN' )], class_ptr ) )
            ## store result in global variable
            self.class_ref.update({
                node.name:{
                    'class_ptr':LabelName( node.name ),
                    'object_list':{},
                    'string_list':{},
                    'super_class':super_name
                }
            })
            new_class_ref = self.class_ref[node.name]
            for fun in node.code.nodes:
                if isinstance( fun, Function ):
                    new_str_label = self.str_label + str( self.str_label_cnt )
                    self.str_label_cnt += 1
                    new_meth_label = self.meth_label + str( self.meth_label_cnt )
                    self.meth_label_cnt += 1
                    ## init scope
                    self.scope.update({
                        new_meth_label:{
                            'vartable':{},
                            'stack':{},
                            'asm_list':[],
                            'stack_cnt':0
                        }
                    })
                    self.scope_list.append( new_meth_label )
                    new_class_ref['string_list'].update( {fun.name:new_str_label} )
                    method_label = Const( LabelName( new_meth_label ) )
                    list0 = CallFunc( Name( 'create_list' ), [self.insert_ast( Const( 0 ), parent_stmt, class_ref )] )
                    fun_ptr = CallFunc( Name( 'create_closure' ), [method_label, list0] )
                    string_label = Const( LabelName( new_str_label ) )
                    parent_stmt.append( CallFunc( Name( 'set_attr' ), [LabelName( node.name ), string_label, fun_ptr] ) )
                    parent_stmt.append( self.insert_ast( fun, parent_stmt, new_class_ref ) )
                else:
                    die( "ERROR: invalid syntax, only function definitions allowed in class body" )
            return 

        elif isinstance( node, Function ):
            self.DEBUG( "Function_insert" )
            code = self.insert_ast( node.code, parent_stmt, class_ref )
            return Function( node.decorators, node.name, node.argnames, node.defaults, node.flags, node.doc, code )

        elif isinstance( node, Return ):
            self.DEBUG( "Return_insert" )
            expr = self.insert_ast( node.value, parent_stmt, class_ref )
            return Return( expr )

        elif isinstance( node, Pass ):
            self.DEBUG( "Pass_insert" )
            return Pass() 
            ##return Return( Name('None') )

        else:
            die( "ERROR: insert_ast: unknown AST node " + str( node ) )


    ## helper for insert_ast
    def lookup_object_ptr( self, nam, class_ref ):
        if nam in class_ref['object_list']:
            return class_ref['object_list'][nam]['obj_ptr']
        elif nam == 'self':
            ## in definition process of a method (nat an actual call)
            return Name(nam)
        else:
            die( "ERROR: trying to access an uninstanciated object: " + nam )

    def lookup_object_class_name( self, nam, class_ref ):
        if nam in class_ref['object_list']:
            return class_ref['object_list'][nam]['class_name']
        else:
            die( "ERROR: trying to access an object of unknown class. obj_name: " + nam )
        
    def lookup_string( self, nam, class_ref ):
        if nam in class_ref['string_list']:
            return class_ref['string_list'][nam]
        else:
            die( "ERROR: trying to access an undefined attribute or method: " + nam )


    ## generate flatten AST
    #######################
    def flatten_ast( self, node, parent_stmt, flat_tmp=None ):
        if isinstance( node, Module):
            self.DEBUG( "Module" )
            return Module( None, self.flatten_ast(node.node, []) )

        elif isinstance( node, Stmt):
            self.DEBUG( "Stmt" )
            stmts = []
            for n in node.nodes:
                self.flatten_ast(n, stmts)
            return Stmt(stmts)

        elif isinstance(node, Add):
            self.DEBUG( "Add" )
            expr = Add( (self.flatten_ast(node.left, parent_stmt), self.flatten_ast(node.right, parent_stmt)) )
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name( new_varname )

        elif isinstance(node, Mul ):
            self.DEBUG( "Mul" )
            expr = Mul( (self.flatten_ast( node.left, parent_stmt ), self.flatten_ast( node.right, parent_stmt )) )
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name( new_varname )

        elif isinstance(node, Sub ):
            self.DEBUG( "Sub" )
            expr = Sub( (self.flatten_ast( node.left, parent_stmt ), self.flatten_ast( node.right, parent_stmt )) )
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name( new_varname )

        elif isinstance(node, Const):
            self.DEBUG( "Const" )
            val = self.check_plain_integer(node.value)
            return Name( self.flatten_ast_add_assign( Const(val), parent_stmt ) )

        elif isinstance(node, Discard):
            self.DEBUG( "Discard" )
            expr = self.flatten_ast( node.expr, parent_stmt )
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return

        elif isinstance(node, AssName ):
            self.DEBUG( "AssName" )
            return node

        elif isinstance( node, Assign ):
            self.DEBUG( "Assign" )
            nodes = self.flatten_ast( node.nodes[0], parent_stmt )
            expr = self.flatten_ast( node.expr, parent_stmt )
            parent_stmt.append( Assign( [nodes], expr ) )
            return

        elif isinstance( node, LabelName ):
            self.DEBUG( "LabelName" )
            return node

        elif isinstance( node, Name ):
            self.DEBUG( "Name" )
            ## because of function names we need to create a new assignment
            expr = Name(node.name)
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name(new_varname)

        elif isinstance( node, CallFunc ):
            self.DEBUG( "CallFunc" )
            attr = []
            for attr_elem in node.args:
                attr.append( self.flatten_ast( attr_elem, parent_stmt ) )
            if node.node.name == "input":
                name = Name( "input_int" )
            else:
                name = node.node
            expr = CallFunc( name, attr )
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name(new_varname)

        elif isinstance( node, Printnl ) or isinstance( node, Print ):
            self.DEBUG( "Printnl" )
            attr = self.flatten_ast(node.nodes[0], parent_stmt)
            parent_stmt.append( CallFunc(Name('print_any'), [attr] ) )
            ## returns nothing because print has no return value
            return

        elif isinstance( node, UnarySub ):
            self.DEBUG( "UnarySub" )
            expr = UnarySub(self.flatten_ast(node.expr, parent_stmt))
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name(new_varname)

        elif isinstance( node, UnaryAdd ):
            self.DEBUG( "UnaryAdd" )
            ## ignore UnaryAdd node and use only its content
            expr = self.flatten_ast(node.expr, parent_stmt)
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name(new_varname)

        elif isinstance(node, LeftShift):
            self.DEBUG( "LeftShift" )
            expr = LeftShift((self.flatten_ast(node.left, parent_stmt), self.flatten_ast(node.right, parent_stmt)))
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name(new_varname)

        elif isinstance(node, RightShift):
            self.DEBUG( "RightShift" )
            expr = RightShift((self.flatten_ast(node.left, parent_stmt), self.flatten_ast(node.right, parent_stmt)))
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name(new_varname)

        elif isinstance( node, Bitand ):
            self.DEBUG( "Bitand" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n, parent_stmt)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = Bitand(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
                elif (cnt > 1):
                    expr = Bitand([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
                cnt += 1
            return Name(new_varname)

        elif isinstance( node, Bitor ):
            self.DEBUG( "Bitor" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n, parent_stmt)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = Bitor(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
                elif (cnt > 1):
                    expr = Bitor([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
                cnt += 1
            return Name(new_varname)

        elif isinstance( node, Bitxor ):
            self.DEBUG( "Bitxor" )
            flat_nodes = []
            cnt = 0
            for n in node.nodes:
                flat_node = self.flatten_ast(n, parent_stmt)
                if (cnt == 0):
                    flat_nodes.append(flat_node)
                elif (cnt == 1):
                    flat_nodes.append(flat_node)
                    expr = Bitxor(flat_nodes)
                    new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
                elif (cnt > 1):
                    expr = Bitxor([Name(new_varname), flat_node])
                    new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
                cnt += 1
            return Name(new_varname)

        elif isinstance (node, Invert ):
            self.DEBUG("Invert")
            expr = Invert(self.flatten_ast(node.expr, parent_stmt) )
            new_varname = self.flatten_ast_add_assign(expr, parent_stmt)
            return Name(new_varname)

        elif isinstance( node, And ):
            self.DEBUG( "And" )
            cnt = 0
            new_varname = None
            for n in node.nodes:
                if cnt == 0:
                    ## first operand
                    flat_node = self.flatten_ast(n, parent_stmt)
                    new_varname = self.flatten_ast_add_assign( flat_node, parent_stmt )
                else:
                    if_body = Assign( [AssName( new_varname, 'OP_ASSIGN' )], n )
                    expr = If( [( CallFunc(Name(self.unbox_int), [Name( new_varname )]), Stmt( [if_body] ) )], None )
                    self.flatten_ast( expr, parent_stmt )
                cnt += 1
            return Name(new_varname)

        elif isinstance( node, Or ):
            self.DEBUG( "Or" )
            cnt = 0
            new_varname = None
            for n in node.nodes:
                if cnt == 0:
                    ## first operand
                    flat_node = self.flatten_ast(n, parent_stmt)
                    new_varname = self.flatten_ast_add_assign( flat_node, parent_stmt )
                else:
                    if_body = Assign( [AssName( new_varname, 'OP_ASSIGN' )], n )
                    expr = If( [( Not(CallFunc(Name(self.unbox_int), [Name( new_varname )]) ), Stmt( [if_body] ) )], None )
                    self.flatten_ast( expr, parent_stmt )
                cnt += 1
            return Name(new_varname)

        elif isinstance( node, Not ):
            self.DEBUG( "Not" )
            expr = Not( self.flatten_ast( node.expr, parent_stmt ) )
            new_varname = self.flatten_ast_add_assign( expr, parent_stmt )
            return Name( new_varname )

        elif isinstance( node, Compare ):
            self.DEBUG( "Compare" )
            cnt = 0
            new_varname = None
            for op in node.ops:
                flat_op = self.flatten_ast(op[1], parent_stmt)
                if cnt == 0:
                    expr = Compare( self.flatten_ast( node.expr, parent_stmt ), [(op[0], flat_op)] )
                elif new_varname != None:
                    expr = Compare( Name( new_varname ), [(op[0], flat_op)] )
                else:
                    die("ERROR: flattening compare, tried to assign to None")
                new_varname = self.flatten_ast_add_assign_bool( expr, op[0], parent_stmt )
                cnt += 1
            return Name( new_varname )

        elif isinstance( node, If ):
            self.DEBUG( "If" )
            ## set end_label
            if flat_tmp != None:
                end_label = flat_tmp
            else:
                self.cond_label_cnt += 1
                end_label = self.cond_label + str(self.cond_label_cnt)
            if len(node.tests) == 0:
                ## recursivity reached end
                if node.else_ is not None:
                    for stmt in node.else_.nodes:
                        self.flatten_ast( stmt, parent_stmt )
                    ## end_label
                    parent_stmt.append( Label( LabelName( end_label ) ) )
            else:
                test1 = node.tests[0]
                ## set false_label
                if node.else_ is None  and len(node.tests) == 1:
                    false_label = end_label
                else:
                    self.cond_label_cnt += 1
                    false_label = self.cond_label + str(self.cond_label_cnt)
                ## if not cond1 goto false_label
                new_varname = self.flatten_ast( Not( test1[0] ), parent_stmt )
                parent_stmt.append( If( [( new_varname, LabelName( false_label ) )], None ) )
                ## statement1 (cond1 is True)
                for stmt in test1[1].nodes:
                    self.flatten_ast( stmt, parent_stmt )
                if node.else_ is not None or len(node.tests) > 1:
                    ## goto end_label
                    parent_stmt.append( Goto( LabelName( end_label ) ) )
                ## start false_label and recoursively flatten If with one test less
                parent_stmt.append( Label( LabelName( false_label ) ) )
                self.flatten_ast( If( node.tests[1:], node.else_ ), parent_stmt, end_label )
            return

        elif isinstance( node, While ):
            self.DEBUG( "While" )
            ## create labels
            self.cond_label_cnt += 1
            top_label = self.cond_label + str(self.cond_label_cnt)
            self.cond_label_cnt += 1
            test_label = self.cond_label + str(self.cond_label_cnt)
            ## goto test
            parent_stmt.append( Goto( LabelName( test_label ) ) )
            ## topLabel:
            parent_stmt.append( Label( LabelName( top_label ) ) )
            ## flatten while body
            for stmt in node.body.nodes:
                self.flatten_ast( stmt, parent_stmt )
            ## testLabel:
            parent_stmt.append( Label( LabelName( test_label ) ) )
            ## flatten condition
            new_varname = self.flatten_ast( node.test, parent_stmt )
            ## test
            parent_stmt.append( If( [( new_varname, LabelName( top_label ) )], None ) )
            return

        elif isinstance( node, Function ):
            self.DEBUG( "Function" )
            code = self.flatten_ast(node.code, parent_stmt)
            expr = Function(node.decorators, node.name, node.argnames, node.defaults, node.flags, node.doc, code)
            parent_stmt.append( expr )
            return

        elif isinstance( node, Return ):
            self.DEBUG( "Return" )
            expr = self.flatten_ast(node.value, parent_stmt)
            return Return( expr )

        elif isinstance( node, Pointer ):
            return node

        elif isinstance( node, Pass ):
            self.DEBUG( "Pass" )
            return Pass() 

        else:
            die( "ERROR: flatten_ast: unknown AST node " + str( node ) )

    ## helper for flatten_ast
    def flatten_ast_add_assign( self, expr, parent_stmt ):
        self.var_counter += 1
        name = self.tempvar + str( self.var_counter )
        nodes = AssName(name, 'OP_ASSIGN')
        parent_stmt.append( Assign( [nodes], expr ) )
        self.DEBUG( "\t\t\tnew statement node: append Assign" + str( name ) )
        return name

    def flatten_ast_add_assign_bool( self, expr, op, parent_stmt ):
        self.var_counter += 1
        name = self.tempvar + str( self.var_counter )
        nodes = AssName( name, 'OP_ASSIGN' )
        parent_stmt.append( AssignBool( [nodes], expr, op ) )
        self.DEBUG( "\t\t\tnew statement node: append AssignBool" + str( name ) )
        return name


    ## convert the flattened AST into a list of ASM expressions
    ###########################################################
    def flatten_ast_2_list( self, nd, scope ):
        if isinstance( nd, Module ):
            self.DEBUG( "Module_asm" )
            self.flatten_ast_2_list( nd.node, scope )
            return

        elif isinstance( nd, Stmt ):
            self.DEBUG( "Stmt_asm" )
            ## program
            new_scope = self.scope[self.scope_list[self.scope_cnt]]
            self.scope_cnt += 1
            for n in nd.nodes:
                self.flatten_ast_2_list( n, new_scope )
            ## special case: return new_scope because Function node needs to assign arguments to this scope
            return new_scope

        elif isinstance( nd, Add ):
            self.DEBUG( "Add_asm" )
            left = self.lookup( nd.left.name, scope )
            right = self.lookup( nd.right.name, scope )
            ret = left
            if self.STACK:
                scope['asm_list'].append( ASM_movl( ret, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
            scope['asm_list'].append( ASM_addl( right, ret ) )
            return ret

        elif isinstance( nd, Sub ):
            self.DEBUG( "Sub_asm" )
            left = self.lookup( nd.left.name, scope )
            right = self.lookup( nd.right.name, scope )
            ret = left
            if self.STACK:
                scope['asm_list'].append( ASM_movl( ret, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
            scope['asm_list'].append( ASM_subl( right, ret ) )
            return ret

        elif isinstance( nd, Mul ):
            self.DEBUG( "Mul_asm" )
            left = self.lookup( nd.left.name, scope )
            right = self.lookup( nd.right.name, scope )
            ret = left
            if self.STACK:
                scope['asm_list'].append( ASM_movl( ret, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
            scope['asm_list'].append( ASM_imull( right, ret ) )
            return ret

        elif isinstance( nd, Bitand ):
            self.DEBUG( "Bitand_asm" )
            left = self.lookup( nd.nodes[0].name, scope )
            right = self.lookup( nd.nodes[1].name, scope )
            ret = left
            if self.STACK:
                scope['asm_list'].append( ASM_movl( ret, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
            scope['asm_list'].append( ASM_andl( right, ret ) )
            return ret

        elif isinstance( nd, Bitor ):
            self.DEBUG( "Bitor_asm" )
            left = self.lookup( nd.nodes[0].name, scope )
            right = self.lookup( nd.nodes[1].name, scope )
            ret = left
            if self.STACK:
                scope['asm_list'].append( ASM_movl( ret, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
            scope['asm_list'].append( ASM_orl( right, ret ) )
            return ret

        elif isinstance( nd, Bitxor ):
            self.DEBUG( "Bitxor_asm" )
            left = self.lookup( nd.nodes[0].name, scope )
            right = self.lookup( nd.nodes[1].name, scope )
            ret = left
            if self.STACK:
                scope['asm_list'].append( ASM_movl( ret, self.reg_list['eax'] ) )
                ret = self.reg_list['eax']
            scope['asm_list'].append( ASM_xorl( right, ret ) )
            return ret

        elif isinstance( nd, Invert ):
            self.DEBUG( "Invert_asm" )
            op = self.lookup( nd.expr.name, scope )
            ret = op
            scope['asm_list'].append( ASM_notl( ret ) )
            return ret

        elif isinstance( nd, UnarySub ):
            self.DEBUG( "UnarySub_asm" )
            op = self.lookup( nd.expr.name, scope )
            ret = op
            scope['asm_list'].append( ASM_negl( ret ) )
            return ret

        elif isinstance( nd, LeftShift ):
            self.DEBUG( "LeftShift_asm" )
            left = self.lookup( nd.left.name, scope )
            right = self.lookup( nd.right.name, scope )
            ## shift needs the shifting value in the register ecx
            ## and is called with %cl
            scope['asm_list'].append( ASM_movl( right, self.reg_list['ecx'] ) )
            ret = left
            scope['asm_list'].append( ASM_shll( ASM_register('cl'), ret ) )
            return ret

        elif isinstance( nd, RightShift ):
            self.DEBUG( "LeftRight_asm" )
            left = self.lookup( nd.left.name, scope )
            right = self.lookup( nd.right.name, scope )
            ## shift needs the shifting value in the register ecx
            ## and is called with %cl
            scope['asm_list'].append( ASM_movl( right, self.reg_list['ecx'] ) )
            ret = left
            scope['asm_list'].append( ASM_shrl( ASM_register('cl'), ret ) )
            return ret

        elif isinstance( nd, Assign ) or isinstance( nd, AssignBool ):
            if isinstance(nd.nodes[0].name, LabelName):
                new_def_elem = self.labeltable_lookup(nd.nodes[0].name.name)
            else:
                nam = nd.nodes[0].name ## just consider the first assignement variable
                new_def_elem = self.lookup( nam, scope, False )
            op = self.flatten_ast_2_list( nd.expr, scope )
            if isinstance( nd, Assign ):
                self.DEBUG( "Assign_asm" )
                if self.STACK:
                    scope['asm_list'].append( ASM_movl( op, self.reg_list['eax'] ) )
                    op = self.reg_list['eax']
                scope['asm_list'].append( ASM_movl( op, new_def_elem ) )
            elif isinstance( nd, AssignBool ):
                self.DEBUG( "AssignBool_asm" )
                scope['asm_list'].append( ASM_movl( ASM_immedeate(0), self.reg_list['edx'] ) )
                ## move condition flag (former operation must be ASM_cond() ) into new_def_elem
                if nd.comp == '<':
                    scope['asm_list'].append( ASM_setl( ASM_register('dl') ) )
                elif nd.comp == '<=':
                    scope['asm_list'].append( ASM_setle( ASM_register('dl') ) )
                elif nd.comp == '>':
                    scope['asm_list'].append( ASM_setg( ASM_register('dl') ) )
                elif nd.comp == '>=':
                    scope['asm_list'].append( ASM_setge( ASM_register('dl') ) )
                elif nd.comp == '==':
                    scope['asm_list'].append( ASM_sete( ASM_register('dl') ) )
                elif nd.comp == '!=':
                    scope['asm_list'].append( ASM_setne( ASM_register('dl') ) )
                else:
                    die( "ERROR: unknown compare operator" )
                scope['asm_list'].append( ASM_movl( self.reg_list['edx'], new_def_elem ) )

            if isinstance( new_def_elem, ASM_v_register ) and new_def_elem.is_new():
                ## new_def_elem was priviously spilled and needs to be moved to the stack
                scope['asm_list'].append( ASM_movl( new_def_elem, self.stack_lookup( new_def_elem.get_name(), scope, False ) ) )
                new_def_elem.set_new( False )
            return

        elif isinstance( nd, CallFunc ):
            self.DEBUG( "CallFunc_asm" )
            ## lhs is name of the function
            ## rhs is name of the temp var for the param tree
            stack_offset = 0
            arg_instrs = []
            for attr in nd.args:
                attr = self.flatten_ast_2_list( attr, scope )
                if self.STACK:
                    arg_instrs.insert(0, ASM_movl( attr, self.reg_list['eax'] ) )
                    #scope['asm_list'].append( ASM_movl( attr, self.reg_list['eax'] ) )
                    attr = self.reg_list['eax']
                arg_instrs.insert(1, ASM_movl( attr, ASM_stack( stack_offset, self.reg_list['esp']) ))
                #scope['asm_list'].append(
                #    ASM_movl( attr, ASM_stack( stack_offset, self.reg_list['esp']) )
                #)
                stack_offset += 4
            scope['asm_list'] += arg_instrs
            if isinstance( nd.node, Pointer ):
                name = self.flatten_ast_2_list( nd.node, scope )
            else:
                name = nd.node
            myCallObj = ASM_call( name.name )
            myCallObj.set_r_def( self.reg_list['eax'] )
            myCallObj.set_r_ignore( self.reg_list['eax'] )
            myCallObj.set_r_ignore( self.reg_list['ecx'] )
            myCallObj.set_r_ignore( self.reg_list['edx'] )
            scope['asm_list'].append( myCallObj )
            return self.reg_list['eax']

        elif isinstance( nd, Discard ):
            self.DEBUG( "Discard_asm" )
            ## discard all below
            return

        elif isinstance( nd, Name ):
            self.DEBUG( "Name_asm" )
            return self.lookup( nd.name, scope )

        elif isinstance( nd, LabelName ):
            self.DEBUG( "LabelName_asm" )
            return self.labeltable_lookup( nd.name )

        elif isinstance( nd, Const ):
            self.DEBUG( "Const_asm" )
            if isinstance(nd.value, LabelName):
                return ASM_immedeate(self.flatten_ast_2_list(nd.value, scope))
            else:
                return ASM_immedeate(nd.value)

        elif isinstance( nd, AssName ):
            ## handled by higher node
            self.DEBUG( "AssName_asm" )
            return

        elif isinstance( nd, Compare ):
            self.DEBUG( "Compare_asm" )
            op1 = nd.ops[0]
            left = self.flatten_ast_2_list( nd.expr, scope )
            right = self.flatten_ast_2_list( op1[1], scope )
            if self.STACK:
                scope['asm_list'].append( ASM_movl( right, self.reg_list['eax'] ) )
                right = self.reg_list['eax']
            scope['asm_list'].append(
                ASM_cmpl( right, left )
            )
            ## no return value needed, this is handeled in AssignBool
            return

        elif isinstance( nd, Not ):
            self.DEBUG( "Not_asm" )
            v_reg = self.flatten_ast_2_list( nd.expr, scope )
            scope['asm_list'].append( ASM_cmpl( ASM_immedeate( 0 ), v_reg ) )
            scope['asm_list'].append( ASM_movl( ASM_immedeate( 0 ), self.reg_list['edx'] ) )
            scope['asm_list'].append( ASM_sete( ASM_register('dl') ) )
            scope['asm_list'].append( ASM_movl( self.reg_list['edx'], v_reg ) )
            return v_reg

        elif isinstance( nd, If ):
            self.DEBUG( "If_asm" )
            ## check if nd.tests[0][0] is true
            scope['asm_list'].append( ASM_cmpl( ASM_immedeate( 0 ), self.flatten_ast_2_list( nd.tests[0][0], scope ) ) )
            scope['asm_list'].append( ASM_jne( self.flatten_ast_2_list( nd.tests[0][1], scope ) ) )
            return

        elif isinstance( nd, Goto ):
            self.DEBUG( "Goto_asm" )
            scope['asm_list'].append( ASM_jmp( self.flatten_ast_2_list( nd.label, scope ) ) )
            return

        elif isinstance( nd, Label ):
            self.DEBUG( "Label_asm" )
            scope['asm_list'].append( ASM_plabel( self.flatten_ast_2_list( nd.name, scope ) ) )
            return

        elif isinstance( nd, Function ):
            self.DEBUG( "Function_asm" )
            ## assign passed arguments to argument names
            child_scope= self.flatten_ast_2_list( nd.code, scope )
            stack_offset = 8
            for argname in nd.argnames:
                target = self.lookup( argname, child_scope, False )
                op = ASM_stack( stack_offset, self.reg_list['ebp'])
                if self.STACK:
                    child_scope['asm_list'].insert( 0, ASM_movl( op, self.reg_list['eax'] ) )
                    child_scope['asm_list'].insert( 1, ASM_movl( self.reg_list['eax'], target ) )
                else:
                    child_scope['asm_list'].insert(0, ASM_movl(op, target) )
                stack_offset += 4
            return

        elif isinstance( nd, Return ):
            self.DEBUG( "Return_asm" )
            child_scope['asm_list'].append( ASM_movl( self.lookup( nd.value, scope ), self.reg_list['eax'] ) )
            return

        elif isinstance( nd, Pointer ):
            self.DEBUG( "Pointer_asm" )
            scope['asm_list'].append( ASM_movl( self.lookup(nd.name, scope ), self.reg_list['eax'] ) )
            return Pointer(ASM_pointer(self.reg_list['eax']))

        elif isinstance( node, Pass ):
            self.DEBUG( "Pass" )
            scope['asm_list'].append( ASM_nop() )
            return
 
        else:
            self.DEBUG( "*** ELSE ***" )
            die( "ERROR: flatten_ast_2_list: unknown AST node " + str( nd ) )
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

    def get_header( self ):
        header = []
        ## asm header
        header.append( ASM_text("text") )
#        header.append( ASM_plabel( self.labeltable_lookup( "LC0" ) ) )
        header.append( ASM_text("ascii \"Compiled with JPSM!\"") )
        for class_name in self.class_ref:
            if class_name != self.init_class:
                header.append( ASM_text("comm", class_name + ",4,4") )
        for class_name in self.class_ref:
            str_list = self.class_ref[class_name]['string_list']
            for str_name in str_list:
                header.append( ASM_plabel( self.labeltable_lookup(str_list[str_name] ) ) )
                header.append( ASM_text("string", "\"" + str_name + "\"" ) ) 
        return header

    def get_prolog( self, stack_cnt, nam ):
        prolog = []
        ## asm prolog
        prolog.append( ASM_text("globl " + nam) )
        prolog.append( ASM_plabel( self.labeltable_lookup( nam ) ) )
        prolog.append( ASM_pushl( self.reg_list['ebp'] ) )
        prolog.append( ASM_movl( self.reg_list['esp'], self.reg_list['ebp'] ) )
        prolog.append( ASM_subl( ASM_immedeate( self.init_stack_mem(stack_cnt) ), self.reg_list['esp'] ) )
        return prolog

    def get_epilog( self ):
        epilog = []
        #epilog.append( ASM_movl( ASM_stack( 0, self.reg_list['ebp'] ), self.reg_list['eax'] ) )
        epilog.append( ASM_leave() )
        epilog.append( ASM_ret() )
        return epilog

    def lookup( self, nam, scope, defined=True ):
        if self.STACK:
            return self.stack_lookup( nam, scope, defined )
        else:
            return self.vartable_lookup( nam, scope, defined )

    def stack_lookup( self, nam, scope, defined=True ):
        if nam not in scope['stack']:
            if defined:
                self.DEBUG('DEBUG: var not found: ' + nam)
#                die( "ERROR: variable %s was not defined" %nam )
            ## var is new -> add a new stack object to the dict
            scope['stack_cnt'] += 4
            new_elem = ASM_stack(0 - scope['stack_cnt'], self.reg_list['ebp'])
            scope['stack'].update({nam:new_elem})
        ## return stack object containing the stack pos
        return scope['stack'][nam]

    def vartable_lookup( self, nam, scope, defined=True ):
        if nam not in scope['vartable']:
            if defined:
                die( "ERROR: variable %s was not defined" %nam )
            ## var is new -> add a new virtual register object to the dict
            new_elem = ASM_v_register( nam )
            scope['vartable'].update({nam:new_elem})
        ## return vartable object
        v_reg = scope['vartable'][nam]
        if v_reg.is_spilled() and defined:
            ## instruction call using the spilled v_reg (not defining)
            stack_pos = self.stack_lookup( v_reg.get_spilled_name(), scope )
            self.var_counter += 1
            new_name = self.tempvar + str(self.var_counter)
            new_elem = ASM_v_register( new_name ) ## new v_register
            scope['vartable'].update({new_name:new_elem})
            scope['asm_list'].append( ASM_movl( stack_pos, new_elem ) )
            v_reg = new_elem
        elif v_reg.is_spilled() and not defined:
            ## instruction call defining the spilled v_reg
            self.var_counter += 1
            new_name = self.tempvar + str(self.var_counter)
            v_reg.set_spilled_name( new_name ) ## indicate to the old v_reg the name of the new v_reg
            new_elem = ASM_v_register( new_name )
            scope['vartable'].update({new_name:new_elem})
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
        for block in self.scope:
            asm_list = self.scope[block]['asm_list']
            scope['asm_list'] = []
            for expr in asm_list:
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
                        scope['asm_list'].append(expr)
                else:
                    scope['asm_list'].append(expr)

## not avaliable anymore since loops and conditionals
#
#    ## liveness analysis
#    ####################
#    def liveness( self ):
#        changed = True
#        live_in = []
#        live_in_old = []
#        live_out = [[]]
#        live_out_old = [[]]
#        for i in range(0, len(self.expr_list), 1):
#            live_in.append([])
#            live_in_old.append([])
#            live_out.append([])
#            live_out_old.append([])
#        while changed:
#            changed = False
#            j = 0
#            last_ignores = []
#            label_list = {}
#            remove_ignores = False
#            for i in range( len(self.expr_list), 0, -1 ):
#                element = self.expr_list[i-1]
#                ## LIVE_in(i) = ( LIVE_out(i) - DEF(i) ) union USE(i)
#                temp_live = self.sub_def_live( element.get_r_def(), list(live_out[j]), live_out[j] )
#                temp_live = self.add_use_live( element.get_r_use(), temp_live )
#                if remove_ignores: ## the iteration before added no ignore elements
#                    temp_live = self.sub_def_live( last_ignores, temp_live )
#                    remove_ignores = False
#                if ( len( temp_live ) > 0 and len( element.get_r_ignore() ) > 0 ):
#                    ## the actual live element has live variables and the asm
#                    ## instruction has some special register handling
#                    temp_live = self.add_use_live( element.get_r_ignore(), temp_live )
#                    remove_ignores = True
#                    last_ignores = element.get_r_ignore()
#                if isinstance(element, ASM_plabel):
#                    ## get all labels from asm list (possible succeeders)
#                    label_list.update({element.label:temp_live})
#                live_in_old[j] = live_in[j]
#                live_in[j] = temp_live
#                ## LIVE_out(i) = union_{j in succ(i)} LIVE_in(j)
#                if isinstance( element, ASM_jmp ):
#                    if element.label not in label_list:
#                        label_list.update({element.label:[]})
#                    succ_union = label_list[element.label]
#                elif isinstance( element, ASM_je ):
#                    if element.label not in label_list:
#                        label_list.update({element.label:[]})
#                    succ_union = self.add_use_live( label_list[element.label], temp_live )
#                else:
#                    succ_union = temp_live
#                live_out_old[j+1] = live_out[j+1]
#                live_out[j+1] = succ_union
#                if self.concat_live(live_out_old[j+1]) != self.concat_live(live_out[j+1]) or self.concat_live(live_in_old[j]) != self.concat_live(live_in[j]):
#                    changed = True
#                j += 1
#        return live_out
#
#    ## helper for liveness
#    def sub_def_live( self, defi, live, live_ptr=None ):
#        is_live = False
#        for oper1 in defi:
#            for oper2 in live:
#                if oper1.get_content().get_name() == oper2.get_content().get_name():
#                    live.remove( oper2 )
#                    is_live = True
#            if not is_live and live_ptr != None:
#                ## the variable was defined but never used
#                ## -> add edges in ig with all live vars just before the def
#                oper1.set_ignore( True )
#                live_ptr.append( oper1 )
#        return live
#
#    def add_use_live ( self, use, live ):
#        save = True
#        for oper1 in use:
#            for oper2 in live:
#                if oper1.get_content().get_name() == oper2.get_content().get_name():
#                    save = False
#            if save:
#                live.append( oper1 )
#        return live
#
#    def concat_live( self, live_elems ):
#        my_live_str = "#live: "
#        for item in live_elems:
#            if not item.is_ignore():
#                ## only print 'ususal' live elements
#                ## (ignore the special cases e.g. with call)
#                my_live_str += str( item ) + " "
#        return my_live_str
#
#
#    ## coloring
#    ###########
#    def create_ig( self, live ): ##lives is define as argument
#        ig = Graph()    ## OJO ig OBJECT = GRAPH CLASS
#        d = {}
#        node_list = {}
#        edge_list = []
#        node_cnt_list = {}
#        for registers in live: ## register are define here, and reg_live
#            ## create nodes del graph
#            for reg_live in registers:
#                reg = reg_live.get_content()###method get_conten,object reg_live.method get_content()
#                if reg.get_name() not in node_list:###method get_name ->reg_live.get_content.get_name??
#                    if isinstance( reg, ASM_register ):
#                        node = Node( reg, reg, False )
#                    else:
#                        node = Node( reg )
#                    node_list.update( {reg.get_name():node} ) ### update the list with the new node
#                    ig.add_node( node ) ### object ig . method add_node graph class
#                    node_cnt_list.update( {node.get_name():0} )
#            ## create edges
#            for reg_live1 in registers: ## reg_live1 defin here
#                reg1 = reg_live1.get_content() ###method get_conten,object reg_live1.method get_content()
#                for reg_live2 in registers:
#                    reg2 = reg_live2.get_content()
#                    node_pair = set([node_list[reg1.get_name()], node_list[reg2.get_name()]]) ##traverse all the live to do the node pair
#                    if (len(node_pair) is 2) and (node_pair not in edge_list):
#                        for edge_node in node_pair:
#                            if( edge_node.get_name() in node_cnt_list ):
#                                node_cnt_list[edge_node.get_name()] += 1
#                        edge_list.append( node_pair )
#                        edge = Edge( node_pair )
#                        ig.add_edge( edge ) ##SENDING DATA TO THE METHOD ADD.EDGE OF THE GRAPG CLASS
#        ig.set_constraint_list( node_cnt_list )
#        return ig
#
#    def color_ig( self, ig ):
#        picked_node = ig.get_most_constraint_node()
#        if picked_node == None:
#            return True
#        picked_node.set_active( False )
#        if not self.color_ig( ig ):
#            return False
#        picked_node.set_active( True )
#        picked = False
#        if isinstance(picked_node.get_content(), ASM_register):
#            picked = True
#        if not picked:
#            ## picked_node contains a v_register
#            for reg_name in self.reg_list:
#                color = self.reg_list[reg_name]
#                if color.is_caller():
#                    pick = True
#                    ## check if another node with the same color is connected
#                    for connected_node in ig.get_connected_nodes( picked_node ):
#                        if connected_node.is_active() and color == connected_node.get_color():
#                            pick = False
#                            break
#                    if pick:
#                        ## no other node with the same color is connected
#                        picked_node.set_color(color)
#                        picked = True
#                        break
#        if not picked:
#            ## spill this node
#            self.DEBUG( "Spilled " + str(picked_node) )
#            picked_node.get_content().set_spilled( True )
#            return False
#        return ig

    ## print
    ########
    def print_asm( self, asm_list, alloc=False ):
        for expr in asm_list:
            if alloc:
                print expr.print_alloc()
            else:
                print str( expr )
#
#    def print_liveness( self, live ):
#        j = len( self.expr_list )
#        for element in self.expr_list:
#            print self.concat_live( live[j] )
#            print str( element )
#            j -= 1
#        print self.concat_live( live[j] )
#
#    def print_ig( self, ig ): ## print the dot file
#        print str(ig)
#
#
    ## debug
    ########
    def DEBUG__print_ast( self, ast ):
        print( "\n-----------------------------------------------------" )
        print( "\nAST\n" )
        dump_ast( ast )
        print( "\n-----------------------------------------------------" )
        print( "\n=====================================================" )

    def DEBUG__print_insert_ast( self, ast ):
        print( "\n-----------------------------------------------------" )
        print( "\nINSERT_AST\n" )
        dump_ast( ast )
        print( "\n-----------------------------------------------------" )
        print( "\n=====================================================" )

    def DEBUG__print_flatten_ast( self, ast ):
        print( "\n-----------------------------------------------------" )
        print( "\nFLATTEN_AST" )
        dump_ast( ast )
        print( "\n-----------------------------------------------------" )
        print( "\n=====================================================" )

    def DEBUG( self, text ):
        if self.DEBUGMODE: print "\t\t%s" % str( text )


## start
if 1 <= len( sys.argv[1:] ):
    DEBUG = False
    CLEANUP_ASM = False
    PRINT_PSEUDO = False
    GEN_PSEUDO = False
    PRINT_STACK = False
    GEN_STACK = False
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
    elif 1 < len( sys.argv[1:] ) and "-stack" in sys.argv:
        GEN_STACK = True
        PRINT_STACK = True
#    elif 1 < len( sys.argv[1:] ) and "-liveness" in sys.argv:
#        GEN_PSEUDO = True
#        GEN_LIVENESS = True
#        PRINT_LIVENESS = True
#    elif 1 < len( sys.argv[1:] ) and "-ig" in sys.argv:
#        GEN_PSEUDO = True
#        GEN_LIVENESS = True
#        GEN_IG = True
#        PRINT_IG = True
#    elif 1 < len( sys.argv[1:] ) and "-ig-color" in sys.argv:
#        GEN_PSEUDO = True
#        GEN_LIVENESS = True
#        GEN_IG = True
#        GEN_IG_COLOR = True
#        PRINT_IG_COLOR = True
#    elif 1 < len( sys.argv[1:] ) and "-alloc" in sys.argv:
#        GEN_PSEUDO = True
#        GEN_LIVENESS = True
#        GEN_IG = True
#        GEN_IG_COLOR = True
#        GEN_ALLOC = True
#        PRINT_ALLOC = True
    else:
        ## use stack as default
        GEN_STACK = True
        PRINT_STACK = True

    ## generate assembler
    compl = Engine( sys.argv[-1], DEBUG, GEN_STACK )
    compl.compileme()

    ## perform liveness/coloring/spilling and generate ig
    liveness = None
    ig = None
    ig_color = None
    if GEN_IG_COLOR:
        ig_color = False
        while True:
            compl.compileme( False )
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
    if PRINT_IG:
        compl.print_ig( ig )
    elif PRINT_IG_COLOR:
        compl.print_ig( ig_color )
    elif PRINT_LIVENESS:
        compl.print_liveness( liveness )
    elif PRINT_PSEUDO:
        compl.print_asm( compl.scope )
    elif PRINT_STACK:
        compl.print_asm( compl.get_header() )
        for block in compl.scope:
            compl.print_asm( compl.get_prolog(compl.scope[block]['stack_cnt'], block) )
            compl.print_asm( compl.scope[block]['asm_list'] )
            compl.print_asm( compl.get_epilog() )
    elif PRINT_ALLOC:
        compl.print_asm( compl.get_header() )
        for block in compl.scope:
            compl.print_asm( compl.get_prolog(compl.scope[block]['stack_cnt'], block) )
            compl.print_asm( compl.scope[block]['asm_list'], True )
            compl.print_asm( compl.get_epilog() )
    else:
        usage()
        die( "ERROR: wrong parametrisation" )

else:
    usage()
