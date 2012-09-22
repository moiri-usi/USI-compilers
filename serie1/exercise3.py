#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
#
# Simon Maurer
# Lothar Rubusch

"""
usage:
        exercise3.py <filepath> <depth>
e.g.
        exercise3.py /etc 2
"""

import sys
import os
import stat
import re

if len( sys.argv[1:] ) < 2:
	print "ERROR, usage:\n" + sys.argv[0] + " <filepath> <depth> ..."
	print "e.g.\n" + sys.argv[0] + " /etc 2"
	sys.exit( 1 )

depth_p = int(sys.argv[2])
path_p = sys.argv[1]

def descendTree(path, depth):
	if depth > 0:
		dirList = os.listdir(path)
		for elem in dirList:
			if path[-1] != "/":
				path += "/"
			elemPath = path + elem
			mode = os.lstat(elemPath).st_mode
			if stat.S_ISDIR(mode):
				print elemPath + "/"
				descendTree(elemPath + "/", depth-1)
			else:
				print elemPath

print path_p
descendTree(path_p, depth_p)

