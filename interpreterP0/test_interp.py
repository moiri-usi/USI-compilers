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

import compiler
import unittest

from interp import *

## unittest test suite
class TestSequenceFunctions( unittest.TestCase ):
    def setUp(self):
         self.intp = Interpreterer()

    def test_Add( self ):
        ast = compiler.parse( "1+2" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 3 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Sub( self ):
        ast = compiler.parse( "2-1" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 1 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Sub__negativevalue( self ):
        ast = compiler.parse( "1-2" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), -1 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Mul( self ):
        ast = compiler.parse( "2*10" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 20 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Div( self ):
        ast = compiler.parse( "10/5" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 2 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Assign( self ):
        ast = compiler.parse('x = 1')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( self.intp.vartable_get( 'x' ), 1 )

        ## test number of executed nodes
        self.assertEqual( 4, res )

    def test_Bitand ( self ):
        ast = compiler.parse('2&1')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 0 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Bitor( self ):
        ast = compiler.parse('2|1')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 3 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Bitxor( self ):
        ast = compiler.parse('3^5')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 6 )

        ## test number of executed nodes
        self.assertEqual( 5, res )

    def test_Name( self ):
        ast = compiler.parse('x')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( self.intp.stack_ans(), 'x' )

        ## test number of executed nodes
        self.assertEqual( 3, res )

    def test_UnarySub( self ):
        ast = compiler.parse('-1')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), -1 )

        ## test number of executed nodes
        self.assertEqual( 4, res )

    def test_UnaryAdd( self ):
        ast = compiler.parse('+1')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 1 )

        ## test number of executed nodes
        self.assertEqual( 4, res )

    def test_multipleInstructions( self ):
        ast = compiler.parse('x = -1; x + 2')
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( int(self.intp.stack_ans()), 1 )

        ## test number of executed nodes
        self.assertEqual( 9, res )

## start
suite = unittest.TestLoader().loadTestsFromTestCase( TestSequenceFunctions )
unittest.TextTestRunner( verbosity=2 ).run( suite )
