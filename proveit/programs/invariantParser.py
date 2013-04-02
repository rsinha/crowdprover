import sys
import ply.lex as lex
import ply.yacc as yacc
from proveit.z3.z3 import *
from proveit.programs.benchmark import *

class InvLexer:
	# List of token names
	tokens = (
		'NUMBER',
		'TRUE',
		'FALSE',
		'ID',
		'OP_LEQ',
		'OP_LE',
		'OP_GEQ',
		'OP_GE',
		'OP_EQ',
		'IMPL',
	)

	# Literals
	literals = ['+','-','*','/','^','(',')','[',']','~','&','|']

	# Regular expression rules for tokens

	def t_TRUE(self,t):
		r'True'
		return t

	def t_FALSE(self,t):
		r'False'
		return t

	def t_ID(self,t):
		r'[a-zA-Z][a-zA-Z0-9_]*'
		return t


	def t_NUMBER(self,t):
		r'\d+'
		# print "This is number"
		t.value = int(t.value)
		return t

	def t_IMPL(self,t):
		r'=>'
		return t

	def t_OP_LEQ(self,t):
		r'<='
		return t

	def t_OP_LE(self,t):
		r'<'
		return t

	def t_OP_GEQ(self,t):
		r'>='
		return t

	def t_OP_GE(self,t):
		r'>'
		return t

	def t_OP_EQ(self,t):
		r'=='
		return t

	# Rule to track line numbers
	def t_newline(self,t):
		r'\n+'
		t.lexer.lineno += len(t.value)

	# A string containing ignored characters (spaces and tabs)
	t_ignore  = ' \t'

	# Error handling rule
	def t_error(self,t):
		# print "Illegal character '%s'" % t.value[0]
		# t.lexer.skip(1)
		raise Exception("Illegal character in input: "+t.value[0])

	# Build the lexer
	def __init__(self,**kwargs):
		self.lexer = lex.lex(module=self,**kwargs)

	# Test the lexer, if required
	def test(self,data):
		self.lexer.input(data)
		while True:
			tok = self.lexer.token()
			if not tok: break
			print tok

############################## PARSER ##############################
class InvParser:
	st = SymbolTable()
	# Create the parser. Takes description of the program to retrieve symbol table
	def __init__(self,description):
		self.st.build(description)
		self.lexer = InvLexer()
		self.tokens = self.lexer.tokens
		self.parser = yacc.yacc(module=self)

	precedence = (
		('right','IMPLICATION'),
		('left','|'),
		('left','&'),
		('right','NEG'),
		('left','COMPARISON'),
	    ('left','+','-'),
	    ('left','*','/'),
	    ('right','^'),
	    ('right','UMINUS'),
	    )

	start = 'bexpr'

	# Rule for simple numbers
	def p_makeZ3_NUMBER(self,p):
		'num : NUMBER'
		p[0] = IntVal(int(p[1]))

	# Rules for True and False atoms
	def p_makeZ3_TRUE(self,p):
		'torf : TRUE'
		p[0] = BoolVal(True)

	def p_makeZ3_FALSE(self,p):
		'torf : FALSE'
		p[0] = BoolVal(False)

	# Rule for simple identifiers
	def p_makeZ3_ID(self,p):
		'identifier : ID'
		iden = p[1]
		# print "ID was detected",p[1]
		if  self.st.exists(iden):
			typ = self.st.getTypeOfId(iden)
			if typ == 'int':
				p[0] = Int(iden)
			elif typ == 'bool':
				p[0] = Bool(iden)
			else:
				raise Exception("Type error for "+iden+". Correct type is "+typ)
		else:
			raise Exception("Unknown Identifier: "+iden)

	# Rule for function application
	def p_makeZ3_FUNAPP(self,p):
		'funapp : ID "(" expr ")"'
		arg = p[3]
		f = p[1]
		if self.st.isFunction(f):
			rettyp = self.st.getReturnType(f)
			if rettyp == 'int':
				func = Function(f,IntSort(),IntSort())
				p[0] = func(arg)
			elif rettyp == 'bool':
				func = Function(f,IntSort(),BoolSort())
				p[0] = func(arg)
			else:
				raise Exception("Unknown return type for function: "+f+". Correct type is "+rettyp)
		else:
			raise Exception("Unknown function: "+f)

	# Rule for array indexing
	def p_makeZ3_ARRINDEX(self,p):
		'arrindex : ID "[" expr "]"'
		index = p[3]
		arr = p[1]
		if self.st.isArray(arr):
			arrtyp = self.st.getArrayType(arr)
			if arrtyp == 'int':
				arrind = Array(arr,IntSort(),IntSort())
				p[0] = arrind[index]
			elif arrtyp == 'bool':
				arrind = Array(arr,IntSort(),BoolSort())
				p[0] = arrind[index]
			else:
				raise Exception("Unknown type of array: "+arr+". Correct type is "+arrtyp)
		else:
			raise Exception("Unknown array: "+arr)

	# Rule for atomic expression - number/identifier/function application/array indexing
	def p_makeZ3_ATOM(self,p):
		'''atom : funapp
				| arrindex
				| identifier
				| num'''
		p[0] = p[1]

	# Rule for numerical expression. The grammar is ambiguous, so precedence rules take care of it
	def p_makeZ3_EXPR(self,p):
		'''expr : expr "^" expr
				| expr "/" expr
				| expr "*" expr
				| expr "+" expr
				| expr "-" expr
				| atom'''
		if len(p) == 2:
			p[0] = p[1]
			# print "Made atom"
		else:
			if p[2] == '^':
				p[0] = p[1]**p[3]
			elif p[2] == '/':
				p[0] = p[1]/p[3]
			elif p[2] == '*':
				p[0] = p[1]*p[3]
			elif p[2] == '+':
				p[0] = p[1]+p[3]
			elif p[2] == '-':
				p[0] = p[1]-p[3]
			else:
				raise Exception("Unknown operator found: "+p[2])

	# Rule for negative expression
	def p_makeZ3_UMINUS(self,p):
		'expr : "-" expr %prec UMINUS'
		p[0] = -p[2]

	# Rule for expression in parentheses
	def p_makeZ3_GROUPEXPR(self,p):
		'expr : "(" expr ")"'
		p[0] = p[2]

	# Rule for comparison of expressions
	def p_makeZ3_COMPEXP(self,p):
		'''compatom : expr OP_LEQ expr %prec COMPARISON
					| expr OP_LE expr %prec COMPARISON
					| expr OP_GEQ expr %prec COMPARISON
					| expr OP_GE expr %prec COMPARISON
					| expr OP_EQ expr %prec COMPARISON'''
		if p[2] == '>=': # Actually is the value of the token at p[2]
			p[0] = p[1]>=p[3]
		elif p[2] == '>':
			p[0] = p[1]>p[3]
		elif p[2] == '<=':
			p[0] = p[1]<=p[3]
		elif p[2] == '<':
			p[0] = p[1]<p[3]
		elif p[2] == '==':
			p[0] = p[1]==p[3]
		else:
			raise Exception("Unknown comparison operator: "+p[2])

	# Rule for boolean atom
	def p_makeZ3_BATOM(self,p):
		'''batom : funapp
				| arrindex
				| identifier
				| compatom
				| torf'''
		p[0] = p[1]

	# Rule for boolean expression
	def p_makeZ3_BEXPR(self,p):
		'''bexpr : bexpr "&" bexpr
				| bexpr "|" bexpr
				| bexpr IMPL bexpr %prec IMPLICATION
				| batom'''
		if len(p)==2:
			p[0] = p[1]
			# print "Made batom"
		else:
			if p[2] == '&':
				p[0] = And(p[1],p[3])
			elif p[2] == '|':
				p[0] = Or(p[1],p[3])
			elif p[2] == '=>':
				p[0] = Implies(p[1],p[3])
			else:
				raise Exception("Unknown boolean operator found: "+p[2])


	# Rule for negation of boolean expression
	def p_makeZ3_NEGATE(self,p):
		'bexpr : "~" bexpr %prec NEG'
		p[0] = Not(p[2])

	# Rule for boolean expression in parentheses
	def p_makeZ3_GROUPBEXPR(self,p):
		'bexpr : "(" bexpr ")"'
		p[0] = p[2]


	# Error rule for syntax errors
	def p_error(self,p):
		raise Exception("Syntax Error")


	# Return pair of values
	# (0,x)  => Successfully parsed invariant, x is a Z3 object
	# (1,x) => Error while parsing, x is the error message

def parseInvariant(s):
	if not s: return (1,"PARSING ERROR: Empty input")
	try:
		p = InvParser("count_up_down")
		psr = p.parser
		result = psr.parse(s)
		return (0,result)
	except Z3Exception, e:
		return (1,"PARSING ERROR: "+e)
	except Exception as e:
		return (1,"PARSING ERROR: "+e.args[0])