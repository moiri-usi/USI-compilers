#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Lothar Rubusch

"""
usage:
        exercise1.py <filepath>
e.g.
        exercise1.py ./input.txt
"""

import sys, re
if len( sys.argv[1:] ) != 1:
	print "ERROR, usage:\n" + sys.argv[0] + " <filename>"
	print "e.g.\n" + sys.argv[0] + " ./input.txt"
	sys.exit( 1 )

path = sys.argv[1]

import os.path
if not os.path.exists( path ):
	print "ERROR, file '%s' does not exist" % path
	sys.exit( 1 )

f = open(path)

text = f.read()
f.close()

wordList = {}
# extract words from file to a list (does not work for characters other than [a-zA-Z])
wordArr = re.findall(r'\b\w+\b', text)
for word in wordArr:
	word = re.sub(r'[0-9]|\W', '', word.lower()) # remove any character other than [a-z]
	if word not in wordList:
		wordList.update({word:0})
	wordList[word] += 1

for i in wordList:
	print i, wordList[i]
