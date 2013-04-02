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
	def programAssertion(self):
		return BoolVal(True)

class Z3ProgramFactory(object):
    def newProgram(self, description):
        if   description == 'count_up_down':  return count_up_down_safe(description)
	else: raise CrowdproverException("Errorcode 2: unknown program description")

class count_up_down_safe(Z3Program):
	def __init__(self,description):
		self.description = description

	def programInfo(self):
		info = {}

		states = {}
		states['x'] = 'integer'
		states['y'] = 'integer'

		loops = {}
		loops[1] = (5,9)

		info['states'] = states
		info['loops'] = loops
		
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
		formula = And(formula, x[9] == x[8])
		formula = And(formula, y[9] == y[8])
		formula = And(formula, x[10] == x[9])
		formula = And(formula, y[10] == y[9])

		print "constructed program formula: ", formula
		return formula

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
			print "constructed loop formula: ", formula
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

	def programAssertion(self):
		x = Int('x')
		y = Int('y')
		n = Int('n')
		return (y == n)

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
