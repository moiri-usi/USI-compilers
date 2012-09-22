class Point(object):
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

	def __str__(self):
		return "%d, %d" % (self.x, self.y)

	def __repr__(self):
		return "Point(%d, %d)" % (self.x, self.y)


p = Point(3,4)
p.move(1,1)
print "%d, %d" % (p.x, p.y)
print str(p) # call __str__
print p # call __repr__

class Point3(Point):
	def __init__(self, x, y, z):
		super(Point3, self).__init__(x, y)
		#Point.__init__(x, y)
		self.z = z

	def __repr__(self):
		return "Point3(%d, %d, %d)" % (self.x, self.y, self.z)

p3 = Point3(1,2,3)
print "%d, %d, %d" % (p3.x, p3.y, p3.z)
print p3
