import compiler
import unittest
from interp import *
#from interp import Interpreterer


"""
USAGE

python ./test_interp.py
"""

class TestSequenceFunctions( unittest.TestCase ):

    def setUp(self):
         self.intp = Interpreterer()

## Likewise, if a tearDown() method is defined, the test runner will invoke that
## method after each test.
    # def tearDown(self):
    #     # TODO

    def test_Add( self ):
        ast = compiler.parse( "1+2" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( self.intp.stack[0], 3 )

        ## test number of executed nodes
        self.assertEqual( 5, res )   

    def test_Sub( self ):
        ast = compiler.parse( "2-1" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( self.intp.stack_peek(), 1 )

        ## test number of executed nodes
        self.assertEqual( 5, res )   

    def test_Sub__negativevalue( self ):
        ast = compiler.parse( "1-2" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( self.intp.stack_peek(), -1 )

        ## test number of executed nodes
        self.assertEqual( 5, res )   

    def test_Mul( self ):
        ast = compiler.parse( "2*10" )
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( self.intp.stack_peek(), 20 )

        ## test number of executed nodes
        self.assertEqual( 5, res )   

    def test_Div( self ):
        ast = compiler.parse( "10/5" ) # TODO test division by zero
        res = self.intp.num_nodes( ast )

        ## test result
        self.assertEqual( self.intp.stack_peek(), 2 )

        ## test number of executed nodes
        self.assertEqual( 5, res )   






# TODO rm
    # def test_shuffle(self):
    #     # make sure the shuffled sequence does not lose any elements
    #     random.shuffle(self.seq)
    #     self.seq.sort()
    #     self.assertEqual(self.seq, range(10))

    #     # should raise an exception for an immutable sequence
    #     self.assertRaises(TypeError, random.shuffle, (1,2,3))

    # def test_choice(self):
    #     element = random.choice(self.seq)
    #     self.assertTrue(element in self.seq)

    # def test_sample(self):
    #     with self.assertRaises(ValueError):
    #         random.sample(self.seq, 20)
    #     for element in random.sample(self.seq, 5):
    #         self.assertTrue(element in self.seq)



## start

## The final block shows a simple way to run the tests. unittest.main() provides
## a command-line interface to the test script. When run from the command line,
## the above script produces an output that looks like this
#if __name__ == '__main__':
#    unittest.main()

## The final block shows a simple way to run the tests. unittest.main() provides
## a command-line interface to the test script. When run from the command line,
## the above script produces an output that looks like this
suite = unittest.TestLoader().loadTestsFromTestCase( TestSequenceFunctions )
unittest.TextTestRunner( verbosity=2 ).run( suite )
