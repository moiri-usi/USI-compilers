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
class Exp(object): pass
class Const(Exp):
  def __init__(self, value):
    self.value = value
class Bin(Exp):
  def __init__(self, left, op, right):
    self.left = left
    self.op = op
    self.right = right

# original grammar:
#
# Exp : Exp + Exp
# Exp : Exp - Exp
# Exp : Exp * Exp
# Exp : Exp / Exp
# Exp : n
# Exp : ( Exp )

# with associativity and precedence fixed:
#
# Exp : Exp + Term
# Exp : Exp - Term
# Exp : Term
# Term : Term * Factor
# Term : Term / Factor
# Term : Factor
# Factor : n
# Factor : ( Exp )

tokens = ( 'PLUS', 'MINUS', 'TIMES', 'DIV', 'INT', 'LP', 'RP' )

def t_INT(t):
  r'(0|[1-9]\d*)'
  t.value = int(t.value)
  return t

t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIV = r'/'
t_LP = r'\('
t_RP = r'\)'

def t_WS(t):
  r'[ \t\n\r\f]+'
  pass

def t_error(t):
  raise SyntaxError("Unknown symbol %r" % (t.value[0],))
  print "Skipping", repr(t.value[0])
  t.lexer.skip(1)

precedence = (
  ('left', 'PLUS', 'MINUS'),
  ('left', 'TIMES', 'DIV'),
)

def p_error(p):
  raise SyntaxError(p)

def p_program(p):
  """Program : Exp"""
  p[0] = p[1]

def p_plus(p):
  """Exp : Exp PLUS Exp"""
  p[0] = Bin(p[1], '+', p[3])

def p_minus(p):
  """Exp : Exp MINUS Exp"""
  p[0] = Bin(p[1], '-', p[3])

def p_times(p):
  """Exp : Exp TIMES Exp"""
  p[0] = Bin(p[1], '*', p[3])

def p_div(p):
  """Exp : Exp DIV Exp"""
  p[0] = Bin(p[1], '/', p[3])

def p_num(p):
  """Exp : INT"""
  p[0] = Const(p[1])

def p_paren(p):
  """Exp : LP Exp RP"""
  p[0] = p[2]


def main():
  try:
    if len(sys.argv) == 3 and sys.argv[1] and sys.argv[1] == '-e':
      x = sys.argv[2]
      Interpreter().eval(x)
    else:
      for arg in sys.argv[1:]:
        f = open(arg)
        if f:
            x = f.read()
            Interpreter().eval(x)
        else:
          die('file not found: ' + f)
  except SyntaxError as ex:
    die(str(ex))

class Interpreter(object):
  def eval(self, text):
    lex.lex()
    lex.input(text)

    # for tok in iter(lex.token, None):
      # print repr(tok.type), repr(tok.value)

    parser = yacc.yacc(start="Program", debug=1)
    t = parser.parse(lexer = lex)

    value = self.interp(t)
    print value

  def interp(self, n):
    def interp(n): return self.interp(n)

    if isinstance(n, Const):
      return n.value
    elif isinstance(n, Bin):
      x = interp(n.left)
      y = interp(n.right)
      if n.op == '+':
        return x + y
      elif n.op == '-':
        return x - y
      elif n.op == '*':
        return x * y
      elif n.op == '/':
        return x / y

    # no matching case
    die('unrecognized AST node ' + str(n))

if __name__ == '__main__':
  main()

