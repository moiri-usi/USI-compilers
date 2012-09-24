import random
import unittest

"""
USAGE

python ./unittest_demo.py


RESOURCES

unittest:
http://docs.python.org/library/unittest.html

asserts:
http://docs.python.org/library/unittest.html#assert-methods

"""

class TestSequenceFunctions( unittest.TestCase ):

## When a setUp() method is defined, the test runner will run that method prior
## to each test.
    def setUp(self):
        self.seq = range(10)

## Likewise, if a tearDown() method is defined, the test runner will invoke that
## method after each test.
#    def tearDown(self):
#        # TODO

## several test cases implemented with exceptions
##
## The three individual tests are defined with methods whose names start with
## the letters test.
## The crux of each test is a call to assertEqual() to check for an expected
## result; assertTrue() to verify a condition; or assertRaises() to verify that
## an expected exception gets raised. These methods are used instead of the
## assert statement so the test runner can accumulate all test results and
## produce a report.
    def test_shuffle(self):
        # make sure the shuffled sequence does not lose any elements
        random.shuffle(self.seq)
        self.seq.sort()
        self.assertEqual(self.seq, range(10))

        # should raise an exception for an immutable sequence
        self.assertRaises(TypeError, random.shuffle, (1,2,3))

    def test_choice(self):
        element = random.choice(self.seq)
        self.assertTrue(element in self.seq)

    def test_sample(self):
        with self.assertRaises(ValueError):
            random.sample(self.seq, 20)
        for element in random.sample(self.seq, 5):
            self.assertTrue(element in self.seq)

## start

## The final block shows a simple way to run the tests. unittest.main() provides
## a command-line interface to the test script. When run from the command line,
## the above script produces an output that looks like this
#if __name__ == '__main__':
#    unittest.main()

## The final block shows a simple way to run the tests. unittest.main() provides
## a command-line interface to the test script. When run from the command line,
## the above script produces an output that looks like this
suite = unittest.TestLoader().loadTestsFromTestCase(TestSequenceFunctions)
unittest.TextTestRunner(verbosity=2).run(suite)




## for commandline, run
# python -m unittest -h

