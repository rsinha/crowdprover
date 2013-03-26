from proveit.programs.models import Program, Invariant
from proveit.z3.z3 import *
from proveit.programs.benchmark import *

def substituteFormula(program_id, inv, line):
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program_id)
	states = programStates(z3program)
	renamedStates = map((lambda s: s + '_proveit_' + str(line)), states)
	stateVars = map((lambda x : Int(x)), states)
	renamedStateVars = map((lambda x : Int(x)), renamedStates)

	new_inv = inv
	for i in range(0,len(stateVars)):
		new_inv = substitute(new_inv, (stateVars[i], renamedStateVars[i]))

	print "invariant before substituition: ", inv
	print "invariant after substituition: ", new_inv
	return new_inv

def checkInvariant(program_id, inv, line):
	print "within checkInvariant"
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program_id)
	formula = z3program.programFormula()
	ssainv = substituteFormula(program_id, inv,line)
	s = Solver()
	s.add(formula)
	s.add(Not(ssainv))
	print "Checking user invariant: ", str(ssainv)
	if s.check() == unsat:
		print "Proved invariant"
		return (True, 0)
	else:
		print "Unable to prove invariant"
		print s.model()
		return (False, s.model())

def checkLoopInvariant(program_id, loop_id, inv, line):
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program_id)
	states = programStates(z3program)
	preStates = map((lambda s: s + '_proveit_pre'), states)
	postStates = map((lambda s: s + '_proveit_post'), states)
	stateVars = map((lambda s : Int(s)), states)
	preStateVars = map((lambda s : Int(s)), preStates)
	postStateVars = map((lambda s : Int(s)), postStates)

	loopEntryLine = loopEntry(z3program, loop_id)
	entryformula = substituteFormula(program_id, inv, loopEntryLine)
	programformula = z3program.programFormula()
	s = Solver()
	s.add(programformula)
	s.add(Not(entryformula))
	if s.check() == sat:
		print "Loop invariant does not hold on entry"
		print s.model()
		return (False, s.model())
	else:
		print "Loop invariant holds on entry. Checking inductively..."


	loopformula = z3program.loopFormula(loop_id)
	precond = inv
	postcond = inv
	for i in range(0,len(states)):
		precond = substitute(precond, (stateVars[i], preStateVars[i]))
		postcond = substitute(postcond, (stateVars[i], postStateVars[i]))

	print "Checking user loop invariant: ", str(Implies(precond,postcond))
	s = Solver()
	s.add(loopformula)
	s.add(Not(Implies(precond, postcond)))
	if s.check() == unsat:
		print "Proved loop invariant"
		return (True, 0)
	else:
		print "Unable to prove loop invariant"
		print s.model()
		return (False, s.model())

def programStates(z3program):
	info = z3program.programInfo()
	states = []
	for state in info['states'].keys():
		states += [state]
	return states

def loopEntry(z3program, loop_id):
	info = z3program.programInfo()
	loops = info['loops']
	return loops[loop_id][0] - 1

def parseUserInvariant(s):
	x = Int('x')
	y = Int('y')
	n = Int('n')
	if s == "x + y == n":
		return (x + y == n)
	elif s == "x == n":
		return (x == n)
	elif s == "x == 0":
		return (x == 0)
	elif s == "y == n":
		return (y == n)
	elif s == "y == 0":
		return (y == 0)
	elif s == "x <= n":
		return (x <= n)
	elif s == "x >= 0":
		return (x >= 0)
	elif s == "y <= n":
		return (y <= n)
	elif s == "y >= 0":
		return (y >= 0)
	elif s == "x > y":
		return (x > y)
	elif s == "x >= y":
		return (x >= y)
	elif s == "x < y":
		return (x < y)
	elif s == "x <= y":
		return (x <= y)
	elif s == "y > x":
		return (y > x)
	elif s == "y < x":
		return (y < x)
	elif s == "y >= x":
		return (y >= x)
	elif s == "y <= x":
		return (y <= x)
	elif s == "True":
		return BoolVal(True)
	elif s == "False":
		return BoolVal(False)
	else:
		raise CrowdproverException("Errorcode 1: Could not parse user invariant")
