#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Lothar Rubusch

"""
usage:
        exercise2.py <filepath> <word1> <word2>
e.g.
        exercise2.py ./input.txt Elvis Software
"""

import sys, re
if len( sys.argv[1:] ) < 2:
	print "ERROR, usage:\n" + sys.argv[0] + " <filepath> <word1> <word2> ..."
	print "e.g.\n" + sys.argv[0] + " ./input.txt bubu Elvis Software"
	sys.exit( 1 )

path = sys.argv[1]
words = sys.argv[2:]

def sortString(str):
	return "".join(sorted(str))

wordsDict = {}
for word in words:
	wordSort = re.sub(r'\W|[0-9]', '', word.lower())
	wordsDict.update({sortString(wordSort):word})

import os.path
if not os.path.exists( path ):
	print "ERROR, file '%s' does not exist" % path
	sys.exit( 1 )

f = open(path)

for line in f.readlines():
	wordSort = re.sub(r'\W|[0-9]', '', line.lower())
	wordSort = sortString(wordSort)
	if wordSort in wordsDict:
		print wordsDict[wordSort], '-', re.sub(r'[\n\r]', '', line)

f.close()

