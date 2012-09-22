#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Lothar Rubusch

"""
usage:
        exercise4.py <filepath>
e.g.
        exercise2.py ./input.txt
"""

class Node(object):
	def __init__(self, key):
		self.key = key
		self.children = []

	def getMatchIdx(self, word):
		i = 1
		matchStr = word[0]
		while re.match(r'%s'%matchStr, self.key) and len(self.key) > i-1 and len(word) > i-1:
			i += 1
			matchStr = word[:i]
		return i-1

	def sortChildren(self):
		self.children.sort(key = lambda x: x.key)

	def appendChild(self, key):
		newChild = Node(key)
		newChild.children.append(Node('-'))
		self.children.append(newChild)


	def add(self, word):
		if 0 == len(word): return
		added = False
		idx = 0
		if self.key != '+':
			idx = self.getMatchIdx(word)
		if (idx > 0) or (self.key == '+'):
			# there was at least one match
			added = True
			if (idx < len(self.key)) and (self.key != '+'):
				#new child with rest of key
				newChildKey = self.key[idx:]
				#change key of this node
				self.key = self.key[:idx]
				self.appendChild(newChildKey)
				if self.key != word:
					del self.children[0]

			if (idx < len(word)) or (self.key == '+'):
				#new child with rest of word
				childAdded = False
				if self.key == '+':
					newChildKey = word
				else:
					newChildKey = word[idx:]
				for child in self.children:
					childAdded = child.add(newChildKey)
					if childAdded:
						break
				if not childAdded:
					#no match in chlidren -> new chlid node
					self.appendChild(newChildKey)

		if self.key == '+' and len(self.children) == 0:
			self.children.append(Node(word))

		self.sortChildren();
		return added

	def printTree(self):
		stack = []
		stack = self.children
		while True:
			if 0 == len( stack ):
				return

			tmpChildren = []
			for item in stack:
				if item.key == '-':
					continue
				print str(item)
				tmpChildren += item.children
			stack = tmpChildren

	def __str__(self):
		return "%s %d" % (self.key, len(self.children))

import sys, re
if len( sys.argv[1:] ) < 1:
	print "ERROR, usage:\n" + sys.argv[0] + " <filepath>"
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
wordArr = re.findall(r'\b\w+\b', text)
tree = []
tree = Node('+')
for word in wordArr:
	word = re.sub(r'[0-9]|\W', '', word.upper())
	tree.add(word)

tree.printTree()
