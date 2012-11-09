#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Josafat Piraquive
# Simon Maurer
# (Lothar Rubusch) contributer for prior steps of the project

"""
USAGE:
$ python ./compile.py ./input.txt

TEST:
$ python ./test_compile.py
"""

import compiler
import unittest
import sys
sys.path.append('../')
print sys.path
from compile import *

## unittest test suite
class TestSequenceFunctions( unittest.TestCase ):
    def setUp(self):
        self.compl = Engine()
        self.temp = self.compl.tempvar

    def test_assign_ast( self ):
        expr = "x = 1"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_assign_flat( self ):
        expr = "x = 1"
        src = "Module(None, Stmt([Assign([AssName('"+ self.temp +"1', 'OP_ASSIGN')], Const(1)), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"1'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_assign_list( self ):
    #     expr = "x = 1"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

    def test_assignvar_ast( self ):
        expr = "x = 1; y = x"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_assignvar_flat( self ):
        expr = "x = 1; y = x"
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(1)), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"1')), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], Name('x')), Assign([AssName('y', 'OP_ASSIGN')], Name('"+self.temp+"2'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_assignvar_list( self ):
    #     expr = "x = 1; y = x"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )


    def test_add_ast( self ):
        expr = "x = 1 + 2"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_add_flat( self ):
        expr = "x = 1 + 2"
        ## t1 = 1
        ## t2 = 2
        ## x = t1+t2
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(1)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], Const(2)), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Add((Name('"+self.temp+"1'), Name('"+self.temp+"2')))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"3'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_add_list( self ):
    #     expr = "x = 1 + 2"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

    def test_nestedExpression1_ast( self ):
        expr = "x = -1 + 2"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_nestedExpression1_flat( self ):
        expr = "x = -1 + 2"
        ## t1 =  1
        ## t2 = -t1
        ## t3 = 2
        ## t4 = t2 + t3
        ## x = t4
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(1)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], UnarySub(Name('"+self.temp+"1'))), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Const(2)), Assign([AssName('"+self.temp+"4', 'OP_ASSIGN')], Add((Name('"+self.temp+"2'), Name('"+self.temp+"3')))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"4'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_nestedExpression1_list( self ):
    #     expr = "x = -1 + 2"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

    def test_nestedExpression2_ast( self ):
        expr = "x = -1 + -(-2 + 3) + 5"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_nestedExpression2_flat( self ):
        expr = "x = -1 + -(-2 + 3) + 5"
        ## t1 = 1
        ## t2 = -t1
        ## t3 = 2
        ## t4 = -t3
        ## t5 = 3
        ## t6 = t4 + t5
        ## t7 = -t6
        ## t8 = t2 + t7
        ## t9 = 5
        ## t10 = t8 + t9
        ## x = t10
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(1)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], UnarySub(Name('"+self.temp+"1'))), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Const(2)), Assign([AssName('"+self.temp+"4', 'OP_ASSIGN')], UnarySub(Name('"+self.temp+"3'))), Assign([AssName('"+self.temp+"5', 'OP_ASSIGN')], Const(3)), Assign([AssName('"+self.temp+"6', 'OP_ASSIGN')], Add((Name('"+self.temp+"4'), Name('"+self.temp+"5')))), Assign([AssName('"+self.temp+"7', 'OP_ASSIGN')], UnarySub(Name('"+self.temp+"6'))), Assign([AssName('"+self.temp+"8', 'OP_ASSIGN')], Add((Name('"+self.temp+"2'), Name('"+self.temp+"7')))), Assign([AssName('"+self.temp+"9', 'OP_ASSIGN')], Const(5)), Assign([AssName('"+self.temp+"10', 'OP_ASSIGN')], Add((Name('"+self.temp+"8'), Name('"+self.temp+"9')))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"10'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_nestedExpression2_list( self ):
    #     expr = "x = -1 - (-2 + 3) + 5"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )


#5

    def test_sub_ast( self ):
        expr = "x = 2 - 1"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_sub_flat( self ):
        expr = "x = 2 - 1"
        ## t1 = 2
        ## t2 = 1
        ## t3 = t1 - t2
        ## x = t3
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(2)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], Const(1)), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Sub((Name('"+self.temp+"1'), Name('"+self.temp+"2')))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"3'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_sub_list( self ):
    #     expr = "x = 2 -1"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )
    
# 6

    
    def test_mul_ast( self ):
        expr = "x = 2 * 10"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_mul_flat( self ):
        expr = "x = 2 * 10"
        ## t1 = 2 
        ## t2 = 10
        ## t3 = t1 * t2
        ## x = t3
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(2)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], Const(10)), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Mul((Name('"+self.temp+"1'), Name('"+self.temp+"2')))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"3'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_mul_list( self ):
    #     expr = "x = 2 * 10"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

##
###7  
##
##    def test_div_ast( self ):
##        expr = "x = 10 / 5"
##        src = str( compiler.parse( expr ) )
##        self.compl.compileme( expr )
##        res = self.compl.DEBUG__print_ast()
##        self.assertEqual( src, res )
##
##    def test_div_flat( self ):
##        expr = "x = 10 / 5"
##        ## t1 = 10 / 5
##        ## x = t1
##        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Div((Const(10), Const(5)))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"1'))]))"
##        self.compl.compileme( expr )
##        res = self.compl.DEBUG__print_flat()
##        self.assertEqual( src, res )
##
##    # def test_div_list( self ):
##    #     expr = "x = 10 / 5"
##    #     src = "some kind of list" #TODO
##    #     self.compl.compileme( expr )
##    #     res = self.compl.DEBUG__print_list()
##    #     self.assertEqual( src, res )
##
##
###8
##
##    def test_UnaryAdd_ast( self ):
##        expr = "x = +5"
##        src = str( compiler.parse( expr ) )
##        self.compl.compileme( expr )
##        res = self.compl.DEBUG__print_ast()
##        self.assertEqual( src, res )
##
##    def test_UnaryAdd_flat( self ):
##        expr = "x = +5"
##        ## t1 = 5
##        ## t2 = -t1
##        ## x = t2
##        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(5)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], UnaryAdd(Name(t1))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"2'))]))"
##        self.compl.compileme( expr )
##        res = self.compl.DEBUG__print_flat()
##        self.assertEqual( src, res )

    # def test_UnaryAdd_list( self ):
    #     expr = "x = +5"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

#9

    def test_UnarySub_ast( self ):
        expr = "x = -5"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_UnarySub_flat( self ):
        expr = "x = -5"
        ## t1 = 5
        ## t2 = -t1
        ## x = t2
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(5)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], UnarySub(Name('"+self.temp+"1'))), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"2'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_UnarySub_list( self ):
    #     expr = "x = -5"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

#10

    def test_BitAnd_ast( self ):
        expr = "x = 0&1"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_BitAnd_flat( self ):
        expr = "x = 0&1"
        ## t1 = 2
        ## t2 = 1
        ## t3 = t1 & t2
        ## x = t3
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(0)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], Const(1)), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Bitand([Name('"+self.temp+"1'), Name('"+self.temp+"2')])), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"3'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_BitAnd_list( self ):
    #     expr = "x = 2&1"
    #     src = "some kind of list" #TODO
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

#11

    def test_BitOr_ast( self ):
        expr = "x = 2|1"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_BitOr_flat( self ):
        expr = "x = 2|1"
        ## t1 = 2
        ## t2 = 1
        ## t3 = t1|t2
        ## x = t3
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(2)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], Const(1)), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Bitor([Name('"+self.temp+"1'), Name('"+self.temp+"2')])), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"3'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_BitOr_list( self ):
    #     expr = "x = 2&1"
    #     src = "some kind of list" #TODO1
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )



    def test_Bitxor_ast( self ):
        expr = "x = 2^1"
        src = str( compiler.parse( expr ) )
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_ast()
        self.assertEqual( src, res )

    def test_Bitxor_flat( self ):
        expr = "x = 2^1"
        ## t1 = 2
        ## t2 = 1
        ## t3 = t1^t2
        ## x = t3
        src = "Module(None, Stmt([Assign([AssName('"+self.temp+"1', 'OP_ASSIGN')], Const(2)), Assign([AssName('"+self.temp+"2', 'OP_ASSIGN')], Const(1)), Assign([AssName('"+self.temp+"3', 'OP_ASSIGN')], Bitxor([Name('"+self.temp+"1'), Name('"+self.temp+"2')])), Assign([AssName('x', 'OP_ASSIGN')], Name('"+self.temp+"3'))]))"
        self.compl.compileme( expr )
        res = self.compl.DEBUG__print_flat()
        self.assertEqual( src, res )

    # def test_Bitxor_list( self ):
    #     expr = "x = 2^1"
    #     src = "some kind of list" #TODO1
    #     self.compl.compileme( expr )
    #     res = self.compl.DEBUG__print_list()
    #     self.assertEqual( src, res )

## TODO: rm
    # def test_Add( self ):
    #     ast = compiler.parse( "x = 1 + 2" )
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 3 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Sub( self ):
    #     ast = compiler.parse( "2-1" )
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 1 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Sub__negativevalue( self ):
    #     ast = compiler.parse( "1-2" )
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), -1 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Mul( self ):
    #     ast = compiler.parse( "2*10" )
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 20 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Div( self ):
    #     ast = compiler.parse( "10/5" )
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 2 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Assign( self ):
    #     ast = compiler.parse('x = 1')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( self.compl.vartable_get( 'x' ), 1 )

    #     ## test number of executed nodes
    #     self.assertEqual( 4, res )

    # def test_Bitand ( self ):
    #     ast = compiler.parse('2&1')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 0 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Bitor( self ):
    #     ast = compiler.parse('2|1')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 3 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Bitxor( self ):
    #     ast = compiler.parse('3^5')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     # FIXME nothing on stack...       
    #     self.assertEqual( int(self.compl.stack_ans()), 6 )

    #     ## test number of executed nodes
    #     self.assertEqual( 5, res )

    # def test_Name( self ):
    #     ast = compiler.parse('x')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( self.compl.stack_ans(), 'x' )

    #     ## test number of executed nodes
    #     self.assertEqual( 3, res )

    # def test_UnarySub( self ):
    #     ast = compiler.parse('-1')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), -1 )

    #     ## test number of executed nodes
    #     self.assertEqual( 4, res )

    # def test_UnaryAdd( self ):
    #     ast = compiler.parse('+1')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 1 )

    #     ## test number of executed nodes
    #     self.assertEqual( 4, res )

    # def test_multipleInstructions( self ):
    #     ast = compiler.parse('x = -1; x + 2')
    #     res = self.compl.num_nodes( ast )

    #     ## test result
    #     self.assertEqual( int(self.compl.stack_ans()), 1 )

    #     ## test number of executed nodes
    #     self.assertEqual( 9, res )

## start
suite = unittest.TestLoader().loadTestsFromTestCase( TestSequenceFunctions )
unittest.TextTestRunner( verbosity=2 ).run( suite )
