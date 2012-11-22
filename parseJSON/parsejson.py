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

  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right
    
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

def p_error(p):
    raise SyntaxError(p)

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
    p[0] = dict()
    p[0].update({p[2]:p[4]})
    if p[5] != None:
        p[0].update(p[5])

def p_object1_content(p):
    """ OBJ1 : COMA STRING DP TERM OBJ1 """
    p[0] = dict()
    p[0].update({p[2]:p[4]})
    if p[5] != None:
        p[0].update(p[5])

def p_object1_end(p):
    """ OBJ1 : CCB """
    p[0] = None

def p_array_start(p):
    """ ARRAY : OSB TERM ARRAY1 """
    p[0] = list(p[2])
    if p[3] != None:
        p[0] += p[3]

def p_array1_content(p):
    """ ARRAY1 : COMA TERM ARRAY1 """
    p[0] = list(p[2])
    if p[3] != None:
        p[0] += p[3]
    
def p_array1_end(p):
    """ ARRAY1 : CSB """
    p[0] = None

def main():

    input_text = sys.stdin.read()
    lex.lex()
    lex.input(input_text)
    parser = yacc.yacc()

    print parser.parse(lexer=lex)

main()

