from proveit.z3.z3 import *


class Z3Program(object):
	def __init__(self, description):
		self.description = description
	def programInfo(self):
		return {}
	def programFormula(self):
		return BoolVal(True)
	def loopFormula(self, loopId):
		return BoolVal(True)
	def loopCondition(self, loopId):
		return BoolVal(True)
	def programAsserts(self):
		return [(0,BoolVal(True))]

class Z3ProgramFactory(object):
	def newProgram(self, description):
		if description == 'count_up_down':
			return count_up_down_safe(description)
		elif description == 'dillig_example':
			return dillig(description)
		elif description == 'sum01':
			return sum01_safe(description)
		else:
			raise CrowdproverException("Errorcode 2: unknown program description")


class sum01_safe(Z3Program):
	def __init__(self,description):
		self.description = description

	def programInfo(self):
		info = {}

		inputs = {}
		inputs['n'] = 'integer'

		states = {}
		states['i'] = 'integer'
		states['sn'] = 'integer'

		loops = {}
		loops[1] = (5,8)

		info['states'] = states
		info['inputs'] = inputs
		info['loops'] = loops
		info['codelines'] = (2,10)
		info['loopids'] = (1,1)

		return info

	def programFormula(self):
		formula = BoolVal(True)
		i = {}
		sn = {}
		n = Int('n')

		for cnt in range(2,10):
			i[cnt] = Int('i' + '_proveit_' + str(cnt))
			sn[cnt] = Int('sn' + '_proveit_' + str(cnt))

		formula = And(formula, i[3] == i[3])
		formula = And(formula, sn[3] == IntVal(0))
		formula = And(formula, i[4] == IntVal(1))
		formula = And(formula, sn[4] == sn[3])
		formula = And(formula, i[9] == i[8])
		formula = And(formula, sn[9] == sn[8])

		return formula

	def programAsserts(self):
		formula = "sn == n*2 | sn == 0"
		return [(9,formula)]

	def loopFormula(self, loopId):
		if loopId == 1:
			formula = BoolVal(True)
			n = Int('n')
			i_pre = Int('i_proveit_pre')
			sn_pre = Int('sn_proveit_pre')
			i_post = Int('i_proveit_post')
			sn_post = Int('sn_proveit_post')
			formula = And(formula, i_pre <= n)
			formula = And(formula, i_post == i_pre + 1)
			formula = And(formula, sn_post == sn_pre + 2)
			return formula
		else:
			raise CrowdproverException("Errorcode 3: unknown loop id")

	def loopCondition(self, loopId):
		if loopId == 1:
			n = Int('n')
			i = Int('i')
			sn = Int('sn')
			return (i <= n)
		else:
			raise CrowdproverException("Errorcode 3: unknown loop id")




class dillig(Z3Program):
	def __init__(self,description):
		self.description = description

	def programInfo(self):
		info = {}

		inputs = {}
		inputs['n'] = 'integer'

		states = {}
		states['i'] = 'integer'
		states['j'] = 'integer'
		states['z'] = 'integer'
		states['x'] = 'integer'
		states['y'] = 'integer'
		states['w'] = 'integer'

		loops = {}
		loops[1] = (5,9)
		loops[2] = (15,22)

		info['states'] =  states
		info['loops'] = loops
		info['codelines'] = (3,24)
		info['loopids'] = (1,2)
		info['inputs'] = inputs

		return info

	def programFormula(self):
		formula = BoolVal(True)
		i = {}
		j = {}
		z = {}
		x = {}
		y = {}
		w = {}
		n = Int('n')

		formula = And(formula, n >= IntVal(0))

		for q in range(3,24):
			i[q] = Int('i' + '_proveit_' + str(q))
			j[q] = Int('j' + '_proveit_' + str(q))
			z[q] = Int('z' + '_proveit_' + str(q))
			x[q] = Int('x' + '_proveit_' + str(q))
			y[q] = Int('y' + '_proveit_' + str(q))
			w[q] = Int('w' + '_proveit_' + str(q))

		formula = And(formula, i[3] == IntVal(1))
		formula = And(formula, j[3] == j[3])
		formula = And(formula, z[3] == z[3])
		formula = And(formula, x[3] == x[3])
		formula = And(formula, y[3] == y[3])
		formula = And(formula, w[3] == w[3])

		formula = And(formula, i[4] == i[3])
		formula = And(formula, j[4] == IntVal(0))
		formula = And(formula, z[4] == z[3])
		formula = And(formula, x[4] == x[3])
		formula = And(formula, y[4] == y[3])
		formula = And(formula, w[4] == w[3])

		formula = And(formula, i[10] == i[9])
		formula = And(formula, j[10] == j[9])
		formula = And(formula, z[10] == (i[9]-j[9]))
		formula = And(formula, x[10] == x[9])
		formula = And(formula, y[10] == y[9])
		formula = And(formula, w[10] == w[9])

		formula = And(formula, i[11] == i[10])
		formula = And(formula, j[11] == j[10])
		formula = And(formula, z[11] == z[10])
		formula = And(formula, x[11] == IntVal(0))
		formula = And(formula, y[11] == y[10])
		formula = And(formula, w[11] == w[10])

		formula = And(formula, i[12] == i[11])
		formula = And(formula, j[12] == j[11])
		formula = And(formula, z[12] == z[11])
		formula = And(formula, x[12] == x[11])
		formula = And(formula, y[12] == IntVal(0))
		formula = And(formula, w[12] == w[11])

		formula = And(formula, i[13] == i[12])
		formula = And(formula, j[13] == j[12])
		formula = And(formula, z[13] == z[12])
		formula = And(formula, x[13] == x[12])
		formula = And(formula, y[13] == y[12])
		formula = And(formula, w[13] == IntVal(0))

		formula = And(formula, i[14] == i[13])
		formula = And(formula, j[14] == IntVal(0))
		formula = And(formula, z[14] == z[13])
		formula = And(formula, x[14] == x[13])
		formula = And(formula, y[14] == y[13])
		formula = And(formula, w[14] == w[13])

		formula = And(formula, i[23] == i[22])
		formula = And(formula, j[23] == j[22])
		formula = And(formula, z[23] == z[22])
		formula = And(formula, x[23] == x[22])
		formula = And(formula, y[23] == y[22])
		formula = And(formula, w[23] == w[22])

		return formula

	def programAsserts(self):
		formula = "x == y"
		return [(23,formula)]

	def loopFormula(self, loopId):
		n = Int('n')
		i_pre = Int('i_proveit_pre')
		j_pre = Int('j_proveit_pre')
		z_pre = Int('z_proveit_pre')
		x_pre = Int('x_proveit_pre')
		y_pre = Int('y_proveit_pre')
		w_pre = Int('w_proveit_pre')
		i_post = Int('i_proveit_post')
		j_post = Int('j_proveit_post')
		z_post = Int('z_proveit_post')
		x_post = Int('x_proveit_post')
		y_post = Int('y_proveit_post')
		w_post = Int('w_proveit_post')
		formula = BoolVal(True)

		if loopId == 1:
			formula = And(formula, j_pre < n)
			formula = And(formula, j_post == j_pre + 1)
			formula = And(formula, i_post == i_pre + 3)
			return formula
		elif loopId == 2:
			formula = And(formula, j_pre < n)
			formula = And(formula, z_post == z_pre + x_pre + y_pre + w_pre)
			formula = And(formula, y_post == y_pre + 1)
			formula = And(formula, x_post == x_pre + (z_post%2))
			formula = And(formula, w_post == w_pre + 2)
			formula = And(formula, j_post == j_pre + 1)
			return formula
		else:
			raise CrowdproverException("Errorcode 3: unknown loop id")

	def loopCondition(self, loopId):
		if loopId == 1:
			j = Int('j')
			n = Int('n')
			return (j<n)
		elif loopId == 2:
			j = Int('j')
			n = Int('n')
			return (j<n)
		else:
			raise CrowdproverException("Errorcode 3: unknown loop id")





class count_up_down_safe(Z3Program):
	def __init__(self,description):
		self.description = description

	def programInfo(self):
		info = {}

		inputs = {}
		inputs['n'] = 'integer'

		states = {}
		states['x'] = 'integer'
		states['y'] = 'integer'

		loops = {}
		loops[1] = (5,9)

		info['states'] = states
		info['inputs'] = inputs
		info['loops'] = loops
		info['codelines'] = (3,11)
		info['loopids'] = (1,1)

		return info

	def programFormula(self):
		formula = BoolVal(True)
		x = {}
		y = {}
		n = Int('n')

		formula = And(formula, n >= IntVal(0))

		for i in range(3,11):
			x[i] = Int('x' + '_proveit_' + str(i))
			y[i] = Int('y' + '_proveit_' + str(i))

		formula = And(formula, x[3] == n)
		formula = And(formula, y[3] == y[3])
		formula = And(formula, x[4] == x[3])
		formula = And(formula, y[4] == IntVal(0))
		formula = And(formula, x[10] == x[9])
		formula = And(formula, y[10] == y[9])

		return formula

	def programAsserts(self):
		formula = "y == n"
		return [(10,formula)]

	def loopFormula(self, loopId):
		if loopId == 1:
			formula = BoolVal(True)
			x_pre = Int('x_proveit_pre')
			y_pre = Int('y_proveit_pre')
			x_post = Int('x_proveit_post')
			y_post = Int('y_proveit_post')
			formula = And(formula, x_pre > IntVal(0))
			formula = And(formula, x_post == x_pre - 1)
			formula = And(formula, y_post == y_pre + 1)
			return formula
		else:
			raise CrowdproverException("Errorcode 3: unknown loop id")

	def loopCondition(self, loopId):
		if loopId == 1:
			x = Int('x')
			y = Int('y')
			return (x > IntVal(0))
		else:
			raise CrowdproverException("Errorcode 3: unknown loop id")


# The SymbolTable class stores symbol tables (which contains all program variables and type information).
# It also provides functions to access a symbol table

##### Symbol Table structure definition #####
# Functions : ("fun", action, type, arity)
### type is the return type
# Variables : (type, action)
# Arrays    : ("arr", action, type, length)
### Array length could be an integer, an integer variable, or -1 (which means unknown)
##### Symbol Table structure definition #####

class SymbolTable:
	symtab = {}
	def build(self,description):
		if description == 'count_up_down':
			self.symtab = { "A"  : ("arr","math.sin","int",30) ,"f"  : ("fun","math.sin","int",1),"g" : ("fun","math.sin","bool",2),"x" : ("int","operator.mul"),"y" : ("int","operator.truediv"),"n" : ("int","operator.truediv")}
		elif description == 'dillig_example':
			self.symtab = {"n" : ("int","operator.truediv"), "i" : ("int","operator.truediv"), "j" : ("int","operator.truediv"), "z" : ("int","operator.truediv"), "x" : ("int","operator.truediv"), "y" : ("int","operator.truediv"), "w" : ("int","operator.truediv")}
		elif description == 'sum01':
			self.symtab = { "A"  : ("arr","math.sin","int",30) ,"f"  : ("fun","math.sin","int",1),"g" : ("fun","math.sin","bool",2),"i" : ("int","operator.mul"),"sn" : ("int","operator.truediv"),"n" : ("int","operator.truediv")}
		else:
			raise CrowdproverException("Errorcode 2: unknown program description")

	# Does iden exist in symtab?
	def exists(self,iden):
		if iden in self.symtab:
			return True
		else:
			return False

	# Get the type for the identifier. Only for simple data types.
	def getTypeOfId(self,iden):
		return self.symtab[iden][0]

	# Does f exist and is a function?
	def isFunction(self,f):
		if (f in self.symtab) & (self.symtab[f][0]=='fun'):
			return True
		else:
			return False

	# Get return type for a function that already exists in symtab
	def getReturnType(self,f):
		return self.symtab[f][2]

	# Does arr exist and is an array?
	def isArray(self,arr):
		if (arr in self.symtab) & (self.symtab[arr][0]=='arr'):
			return True
		else:
			return False

	# Get type of an array that already exists in symtab
	def getArrayType(self,arr):
		return self.symtab[arr][2]
