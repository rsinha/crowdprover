import sys
import ply.lex as lex
import ply.yacc as yacc
from proveit.z3.z3 import *
from proveit.programs.benchmark import *


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

def t_TRUE(t):
	r'True'
	return t

def t_FALSE(t):
	r'False'
	return t

def t_ID(t):
	r'[a-zA-Z][a-zA-Z0-9_]*'
	return t


def t_NUMBER(t):
	r'\d+'
	# print "This is number"
	t.value = int(t.value)
	return t

def t_IMPL(t):
	r'=>'
	return t

def t_OP_LEQ(t):
	r'<='
	return t

def t_OP_LE(t):
	r'<'
	return t

def t_OP_GEQ(t):
	r'>='
	return t

def t_OP_GE(t):
	r'>'
	return t

def t_OP_EQ(t):
	r'=='
	return t

# Rule to track line numbers
def t_newline(t):
	r'\n+'
	t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t'

# Error handling rule
def t_error(t):
	# print "Illegal character '%s'" % t.value[0]
	# t.lexer.skip(1)
	raise Exception("Illegal character in input: "+t.value[0])

# Build the lexer
lexer = lex.lex()

# This part is to test the lexer. Must be removed eventually.
# data = '''
# true troo
# '''

# lexer.input(data)

# # Tokenize
# while True:
# 	tok = lexer.token()
# 	if not tok: break
# 	print tok.value

############################## PARSER ##############################

# A simple symbol table for the program
# Functions : ("fun", action, type, arity)
### type is the return type
# Variables : (type, action)
# Arrays    : ("arr", action, type, length)
### Array length could be an integer, an integer variable, or -1 (which means unknown)
symtab = { "f"  : ("fun","math.sin","int",1),
            "g" : ("fun","math.sin","bool",2),
            "x" : ("int","operator.mul"),
            "y" : ("int","operator.truediv"),
            "n" : ("int","operator.pow"),
            "A" : ("arr","operator.add","int","n"),
            "p" : ("bool","operator.sub") }

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
def p_makeZ3_NUMBER(p):
	'num : NUMBER'
	p[0] = IntVal(int(p[1]))

# Rules for True and False atoms
def p_makeZ3_TRUE(p):
	'torf : TRUE'
	p[0] = BoolVal(True)

def p_makeZ3_FALSE(p):
	'torf : FALSE'
	p[0] = BoolVal(False)

# Rule for simple identifiers
def p_makeZ3_ID(p):
	'identifier : ID'
	iden = p[1]
	# print "ID was detected",p[1]
	if iden in symtab:
		typ = symtab[iden][0]
		if typ == 'int':
			p[0] = Int(iden)
		elif typ == 'bool':
			p[0] = Bool(iden)
		else:
			raise Exception("Type error for "+iden+". Correct type is "+typ)
	else:
		raise Exception("Unknown Identifier: "+iden)

# Rule for function application
def p_makeZ3_FUNAPP(p):
	'funapp : ID "(" expr ")"'
	arg = p[3]
	f = p[1]
	if (f in symtab) and (symtab[f][0]=='fun'):
		rettyp = symtab[f][2]
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
def p_makeZ3_ARRINDEX(p):
	'arrindex : ID "[" expr "]"'
	index = p[3]
	arr = p[1]
	if (arr in symtab) and (symtab[arr][0]=='arr'):
		arrtyp = symtab[arr][2]
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
def p_makeZ3_ATOM(p):
	'''atom : funapp
			| arrindex
			| identifier
			| num'''
	p[0] = p[1]

# Rule for numerical expression. The grammar is ambiguous, so precedence rules take care of it
def p_makeZ3_EXPR(p):
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
def p_makeZ3_UMINUS(p):
	'expr : "-" expr %prec UMINUS'
	p[0] = -p[2]

# Rule for expression in parentheses
def p_makeZ3_GROUPEXPR(p):
	'expr : "(" expr ")"'
	p[0] = p[2]

# Rule for comparison of expressions
def p_makeZ3_COMPEXP(p):
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
def p_makeZ3_BATOM(p):
	'''batom : funapp
			| arrindex
			| identifier
			| compatom
			| torf'''
	p[0] = p[1]

# Rule for boolean expression
def p_makeZ3_BEXPR(p):
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
def p_makeZ3_NEGATE(p):
	'bexpr : "~" bexpr %prec NEG'
	p[0] = Not(p[2])

# Rule for boolean expression in parentheses
def p_makeZ3_GROUPBEXPR(p):
	'bexpr : "(" bexpr ")"'
	p[0] = p[2]


# Error rule for syntax errors
def p_error(p):
	raise Exception("Syntax Error")

# Build the parser
parser = yacc.yacc()

# while True:
# 	try:
# 		s = raw_input('input > ')
# 	except EOFError:
# 		break
# 	if not s: continue
# 	try:
# 		result = parser.parse(s)
# 		print result
# 	except Z3Exception, e:
# 		print "The entered invariant caused the following error:",e
# 	except Exception as e:
# 		print "PARSING ERROR:",e.args[0]

# Return pair of values
# (0,x)  => Successfully parsed invariant, x is a Z3 object
# (1,x) => Error while parsing, x is the error message
def parseInvariant(s):
	if not s: return (1,"PARSING ERROR: Empty input")
	try:
		result = parser.parse(s)
		return (0,result)
	except Z3Exception, e:
		return (1,"PARSING ERROR: "+e)
	except Exception as e:
		return (1,"PARSING ERROR: "+e.args[0])