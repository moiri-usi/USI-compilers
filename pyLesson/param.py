from sys import argv
import re

for a in argv[1:]: #do not print filename
	b = re.sub(r'\d+', '', a)
	print a, b
