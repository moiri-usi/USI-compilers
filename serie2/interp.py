# get file path from param
import sys
if len( sys.argv[1:] ) != 1:
    print "ERROR, usage:\n" + sys.argv[0] + " <filename>"
    print "e.g.\n" + sys.argv[0] + " ./input.txt"
    sys.exit( 1 )

path = sys.argv[1]

import os.path
if not os.path.exists( path ):
    print "ERROR, file '%s' does not exist" % path
    sys.exit( 1 )

# parse file and generate ast
import compiler
ast = compiler.parseFile(path)

# function to interprete the ast
# @param obj n: node of the ast
def num_nodes(n):
    if isinstance(n, compiler.ast.Module):
        return num_nodes(n.node)

    elif isinstance(n, compiler.ast.Stmt):
        return 1 + sum([num_nodes(x) for x in n.nodes])

    elif isinstance(n, compiler.ast.Add):
        return 1 + num_nodes(n.left) + num_nodes(n.right)
    #Mul
    #Sub
    #Div
    #AssName
    #Bitand
    #Bitor
    #Bitxor
    #CallFunc
    #List
    #Name
    #Println
    #UnarySub
    #UnaryAdd
    else:
        pass
# interprete ast
num_nodes(ast)
