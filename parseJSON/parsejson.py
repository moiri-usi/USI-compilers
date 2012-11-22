#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Josafat Piraquive
# used the "PLY example" proposed by Nate Nystrom as template

import sys, re
from ply import lex, yacc

# error reporting
def die(msg, lineno=None):
  if lineno:
    sys.stderr.write('interpreter error: line ' + str(lineno) + ': ' + msg + '\n')
  else:
    sys.stderr.write('interpreter error: ' + msg + '\n')
  sys.exit(1)

# AST classes
##class Exp(object): pass
##class Const(Exp):
##  def __init__(self, value):
##    self.value = value
##class Bin(Exp):


  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right
    
##OBJ  -> {STR:TERM OBJ'
##OBJ' -> ,STR:TERM
##OBJ' -> }
##TERM  -> [TERM TERM'
##TERM' -> ,TERM
##TERM' -> ]
##TERM  -> STR
##TERM  -> NUM
##TERM  -> BOOL
##TERM  -> NULL

#OSB -> [
#CSB ->  ]
#OCB -> {
#CCB ->  }
#COMA -> ,
#DP -> :

 
tokens = ( 'OSB', 'CSB', 'OCB', 'CCB', 'COMA', 'DP', 'NUMBER', 'BOOLEAN', 'STRING', 'NULL' )

#### Regular expressions for token!!!!! we are young!!!....

t_OSB = r'\['
t_CSB = r'\]'
t_OCB = r'\{'
t_CCB = r'\}'
t_COMA = r'\,'
t_DP = r'\:'
t_NUMBER = r'(0|[1-9][0-9]*)?\.?[0-9]+((e|E)(\+|-)?[1-9][0-9]*)?'
t_BOOLEAN = r'(true|false)'
t_STRING = r'"([^"\\]|\\("|\\))*"'
t_NULL = r'null'

def t_WS(t): ## delete white and other spaces !!! a set the world!!!!!!!!!
  r'[ \t\n\r\f]+'
  pass

def t_error(t):
  raise SyntaxError("Unknown symbol %r" % (t.value[0],))
  print "Skipping", repr(t.value[0])
  t.lexer.skip(1)


"""
OBJ : OCB ATTR CCB
ATTR : STRING DP TERM ATTR1
ATTR1 : COMA STRING DP TERM ATTR1
ATTR1 : EMPTY
TERM : ARRAY
TERM : NUMBER
TERM : STRING
TERM : BOOLEAN
TERM : NULL
ARRAY : OSB ELEMT CSB
ELEMT : TERM ELEMNT1 
ELEMT1 : COMA TERM ELEMT1 
ELEMT1 : EMPTY
"""

## TERM : OBJ
## TERM : ARRAY
## TERM : STRING
## TERM : NUMBER
## TERM : BOOLEAN
## TERM : NULL
## OBJ : {STR:TERM OBJ1
## OBJ1 : ,STR:TERM OBJ1
## OBJ1 : }
## ARRAY : [TERM ARRAY1
## ARRAY1 : ,TERM ARRAY1
## ARRAY1 : ]

##OBJ -> {STR:TERM OBJ'
##OBJ' -> ,STR:TERM OBJ'
##OBJ' -> }
##TERM -> [TERM TERM'
##TERM' -> ,TERM TERM'
##TERM' -> ]
##TERM -> STR
##TERM -> NUM
##TERM -> BOOL
##TERM -> NULL
##TERM -> OBJ

def p_error(p):
    raise SyntaxError(p)

## TERM : OBJ
## TERM : ARRAY
## TERM : STRING
## TERM : NUMBER
## TERM : BOOLEAN
## TERM : NULL
## OBJ : {STR:TERM OBJ1
## OBJ1 : ,STR:TERM OBJ1
## OBJ1 : }
## ARRAY : [TERM ARRAY1
## ARRAY1 : ,TERM ARRAY1
## ARRAY1 : ]

def p_term_object(p):
    """ TERM : OBJ """
    p[0] = p[1]

def p_term_array(p):
    """ TERM : ARRAY """
    p[0] = p[1]

def p_term_string(p):
    """ TERM : STRING """
    p[0] = p[1]

def p_term_number(p):
    """ TERM : NUMBER """
    p[0] = p[1]

def p_term_boolean(p):
    """ TERM : BOOLEAN """
    p[0] = p[1]

def p_term_null(p):
    """ TERM : NULL """
    p[0] = p[1]

def p_object_start(p):
    """ OBJ : OCB STRING DP TERM OBJ1 """
    p[0] = dict(p[2])

def p_object1_content(p):
    """ OBJ1 : COMA STRING DP TERM OBJ1 """
    p[0].update({p[2]:p[4]})

def p_object1_end(p):
    """ OBJ1 : CCB """
    pass

def p_array_start(p):
    """ ARRAY : OSB TERM ARRAY1 """
    p[0] = list(p[2])

def p_array1_content(p):
    """ ARRAY1 : COMA TERM """
    p[0].append(p[2])
    
def p_array1_end(p):
    """ ARRAY1 : CSB """
    pass

def main():

    input_text = sys.stdin.read()
    lex.lex()
    lex.input(input_text)
    parser = yacc.yacc()

    print parser.parse(lexer=lex)

 

##def main():
##  try:
##    if len(sys.argv) == 3 and sys.argv[1] and sys.argv[1] == '-e':
##      x = sys.argv[2]
##      Interpreter().eval(x)
##    else:
##      for arg in sys.argv[1:]:
##        f = open(arg)
##        if f:
##            x = f.read()
##            interp = Interpreter()
##            interp.eval(x)   ##   Interpreter().eval(x)
##        else:
##          die('file not found: ' + f)
##  except SyntaxError as ex:
##    die(str(ex))

##class Interpreter(object):
##
##
##
##  def eval(self, text):
##    lex.lex()
##    lex.input(text)
##
##    # for tok in iter(lex.token, None):
##      # print repr(tok.type), repr(tok.value)
##
##    parser = yacc.yacc(start="Program", debug=1)
##    t = parser.parse(lexer = lex)
##
##    value = self.interp(t)
##    print value
##
##  def interp(self, n):
##    def interp(n): return self.interp(n)
##
##    if isinstance(n, Const):
##      return n.value
##    elif isinstance(n, Bin):
##      x = interp(n.left)
##      y = interp(n.right)
##      if n.op == '+':
##        return x + y
##      elif n.op == '-':
##        return x - y
##      elif n.op == '*':
##        return x * y
##      elif n.op == '/':
##        return x / y
##
##    # no matching case
##    die('unrecognized AST node ' + str(n))
main()

