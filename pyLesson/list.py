a = [1,2,3,4]
print "one element of list"
print a[0]
print "whole list"
for i in a:
	print i

print "index 1 to 2"
for i in a[1:3]:
	print i

print "everything beginning with index 1"
for i in a[1:]:
	print i

print "everything except last index"
for i in a[:-1]:
	print i

print "index 1 to second last index"
for i in a[1:-1]:
	print i

b = map(str, a)
print "map on list with lambda"
c = map(lambda x: x+1, a)
for i in c:
	print i
print "filter on list with lambda"
d = filter(lambda x: x < 3, a)
for i in d:
	print i

