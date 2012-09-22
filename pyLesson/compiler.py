import compiler

ast = compiler.parse("""
x = - input()
print x + input()
""")

print ast

def num_nodes(n):
	if isinstance(n, Module):
		return num_nodes(n.node)

	elif isinstance(n, Stmt):
		"""
		couut = 0
		for child in n.nodes:
			count += num_nodes(child)
		return count
		"""
		return 1 + sum([num_nodes(x) for x in n.nodes])

	elif isinstance(n, Add):
		return 1 + num_nodes(n.left) + num_nodes(n.right)

	else:
		pass

