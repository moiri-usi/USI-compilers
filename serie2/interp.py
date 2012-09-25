# get file path from param
import sys
import os.path
import compiler

"""
USAGE:

python ./interp.py ./input.txt

TEST
python ./test_interp.py
"""


def die( meng ):
    print meng
    sys.exit( -1 )

class Interpreterer( object ):
    def __init__( self, filepath=None ):
        if filepath:
            if not os.path.exists( filepath ):
                die( "ERROR: file '%s' does not exist" % filepath )
            else:
                self.ast = compiler.parseFile( filepath )
        self.stack = []
        self.vartable = {}

    def interpret_file( self ):
        try:
            return self.num_nodes( self.ast )
        except AttributeError:
            die( "ERROR: class started in DEBUG mode, no AST file set" )

    def stack_push( self, elem):
        self.stack.append( elem )

    def stack_pop( self ):
        return self.stack.pop()

    def stack_peek( self ):
        try:
            return self.stack[0]
        except IndexError:
            # TODO check raise
            raise IndexError( "ERROR: stack index error" )

    def vartable_set( self, name, val ):
        self.vartable.update( {name:val} )

    def vartable_get( self, name ):
        try:
            return self.vartable[key]
        except KeyError:
            die( "ERROR: variable '%s' does not exist" % key )

    def num_child_nodes( self, node ):
        num = sum([self.num_nodes(x) for x in node.getChildNodes()])
        return num

    ## function to interprete the ast
    ## @param obj n: node of the ast
    def num_nodes(self, node):
        if isinstance( node, compiler.ast.Module):
            print "\tModule" 
            # flush stack
            self.stack = []
            # flush vartable
            self.vartable = {}
            return self.num_nodes(node.node)

        elif isinstance( node, compiler.ast.Stmt):
            print "\t\tStmt" 
            ## loop over all nodes, thereby execute node operation, construct
            ## list of nodes to count num of nodes as return value of "num_nodes()"
            try:
                num = 1 + self.num_child_nodes( node )
                return num
            except:
                print "ERROR: None Type received, one node returned NOTHING"
                return -1

        elif isinstance(node, compiler.ast.Add):
            print "\t\tAdd" 
            num = 1 + self.num_child_nodes( node )
            self.stack_push( self.stack_pop() + self.stack_pop() )
            return num

        elif isinstance(node, compiler.ast.Mul ):
            print "\t\tMul" 
            num = 1 + self.num_child_nodes( node )
            self.stack_push( self.stack_pop() * self.stack_pop() )
            return num

        elif isinstance(node, compiler.ast.Sub ):
            print "\t\tSub" 
            num = 1 + self.num_child_nodes( node )
            var_a = self.stack_pop()
            var_b = self.stack_pop()
            self.stack_push( var_b - var_a )
            return num

        elif isinstance(node, compiler.ast.Div ):
            print "\t\tDiv" 
            num = 1 + self.num_child_nodes( node )
            var_a = self.stack_pop()
            var_b = self.stack_pop()
#            print "XXX num '%d', var_a '%d', var_b '%d'" % (num, var_a, var_b)   
            try: # FIXME, exit on ZeroDivisionError
                self.stack_push( var_b / var_a )
            except ZeroDivisionError:
                die( "ERROR: division by 0" )
            return num

        elif isinstance(node, compiler.ast.Const):
            print "\t\tConst" 
            ## TODO const flag, no assingment to const
            if type( node.value ) is not int:
                print "WARNING: casting float to integer"  
                node.value = int( node.value )
            self.stack_push( node.value )
            return 1

        elif isinstance(node, compiler.ast.Discard):
            print "\t\tDiscard" 
            return 1 + self.num_child_nodes( node )

        elif isinstance(node, compiler.ast.AssName ):
            return 1    

        elif isinstance(node, compiler.ast.Assign ):
            return 1    

        elif isinstance(node, compiler.ast.Bitand ):
            return 1    

        elif isinstance(node, compiler.ast.Bitor ):
            return 1    

        elif isinstance(node, compiler.ast.Bitxor ):
            return 1    

        elif isinstance(node, compiler.ast.CallFunc ):
            return 1    

        elif isinstance(node, compiler.ast.List ):
            return 1    

        elif isinstance(node, compiler.ast.Name ):
            return 1    

        elif isinstance(node, compiler.ast.Printnl ):
            print "\t\tPrintnl"
            num = 1 + self.num_child_nodes( node )
            print "%s" % str( self.stack_pop() )
            return num

        elif isinstance(node, compiler.ast.UnarySub ):
            return 1    

        elif isinstance(node, compiler.ast.UnaryAdd ):
            return 1    

        else:
            print "unknown ast node"
            return 1

## start
if 1 == len( sys.argv[1:] ):
    inst = Interpreterer( sys.argv[1] )
    number_of_nodes = inst.interpret_file()

