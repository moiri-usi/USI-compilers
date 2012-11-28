#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Josafat Piraquive
# used the "PLY example" proposed by Nate Nystrom as template

import sys, re, json
from ply import lex, yacc

# error reporting
def die(msg, lineno=None):
    if lineno:
        sys.stderr.write('ERROR: line ' + str(lineno) + ': ' + msg + '\n')
    else:
        sys.stderr.write(msg + '\n')
    sys.exit(1)
    
#OSB -> [
#CSB ->  ]
#OCB -> {
#CCB ->  }
#COMA -> ,
#DP -> :
tokens = ( 'OSB', 'CSB', 'OCB', 'CCB', 'COMA', 'DP', 'FLOAT', 'INT', 'BOOLEAN', 'STRING', 'NULL' )

#### Regular expressions for token!!!!! we are young!!!....

def t_STRING(t):
    r'"([^"\\]|\\("|\\|/|b|f|n|r|t|u[0-9a-fA-F][0-9a-fA-F][0-9a-fA-F][0-9a-fA-F]))*"'
    t.value = t.value[1:-1].decode('string-escape')
    return t

def t_FLOAT(t):
    r'(-?(0|[1-9][0-9]*))(((\.[0-9]+)((e|E)(-|\+)?[0-9]*)?)|((e|E)(-|\+)?[0-9]+))'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'((\+|-)?[1-9][0-9]*)|0'
    t.value = int(t.value)
    return t

def t_BOOLEAN(t):
    r'(true|false)'
    if t.value == "true":
        t.value = True
    else:
        t.value = False
    return t

def t_NULL(t):
    r'null'
    t.value = None
    return t

t_OSB = r'\['
t_CSB = r'\]'
t_OCB = r'\{'
t_CCB = r'\}'
t_COMA = r'\,'
t_DP = r'\:'

def t_WS(t): ## delete white and other spaces !!! and set the world!!!!!!!!!
    r'[ \t\n\r\f]+'
    pass

def t_error(t):
    raise SyntaxError("Unknown symbol %r" % (t.value[0],))
    #raise SyntaxError("No JSON object could be decoded")
    print "Skipping", repr(t.value[0])
    t.lexer.skip(1)

## TERM : OBJ
## TERM : ARRAY
## TERM : STRING
## TERM : FLOAT
## TERM : INT
## TERM : BOOLEAN
## TERM : NULL
## OBJ : {ATTR OBJ1
## OBJ1 : ,STR:TERM OBJ1
## OBJ1 : }
## ATTR : STR:TERM
## ATTR : 
## ARRAY : [ITEM ARRAY1
## ARRAY1 : ,TERM ARRAY1
## ARRAY1 : ]
## ITEM : TERM
## ITEM :

def p_error(p):
    raise SyntaxError("Unexpected Token: " + str(p))

def p_term(p):
    """ TERM    : OBJ
                | ARRAY
                | STRING
                | FLOAT
                | INT
                | BOOLEAN
                | NULL """
    p[0] = p[1]

def p_object_start(p):
    """ OBJ : OCB ATTR OBJ1 """
    p[0] = dict()
    if p[2] != None:
        p[0].update(p[2])
    if p[3] != None:
        p[0].update(p[3])

def p_attr_term(p):
    """ ATTR : STRING DP TERM """
    p[0] = {p[1]:p[3]}

def p_attr_(p):
    """ ATTR : """
    p[0] = None

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
    """ ARRAY : OSB ITEM ARRAY1 """
    p[0] = []
    if p[2] != None:
        p[0] += p[2]
    if p[3] != None:
        p[0] += p[3]

def p_array1_content(p):
    """ ARRAY1 : COMA TERM ARRAY1 """
    p[0] = [p[2]]
    if p[3] != None:
        p[0] += p[3]
    
def p_array1_end(p):
    """ ARRAY1 : CSB """
    p[0] = None

def p_item_term(p):
    """ ITEM : TERM """
    p[0] = [p[1]]

def p_item_(p):
    """ ITEM : """
    p[0] = None

def main():
    input_text = sys.stdin.read()
    try:
        lex.lex()
        lex.input(input_text)
        parser = yacc.yacc()
        json_obj = parser.parse(lexer=lex)
    except SyntaxError as ex:
        die(str(ex))
#    if json.loads(input_text) == json_obj: 
#        print json.dumps(json_obj, sort_keys=True, indent=4)
#    else:
#        print "not equal to json.loads"

    print json.dumps(json_obj, sort_keys=True, indent=4)

main()

