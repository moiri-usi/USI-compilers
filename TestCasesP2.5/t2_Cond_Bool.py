a = 6
b = 7
c = 42
print 1, a == 6
print 2, a == 7
print 3, a == 6 and b == 7
print 4, a == 7 and b == 7
print 5, not a == 7 and b == 7
print 6, a == 7 or b == 7
print 7, a == 7 or b == 6
print 8, not (a == 7 and b == 6)
print 9, not a == 7 and b == 6

### http://en.wikibooks.org/wiki/Non-Programmer's_Tutorial_for_Python_2.6/Boolean_Expressions

"""
1 True
2 False
3 True
4 False
5 True
6 True
7 False
8 True
9 False
"""
