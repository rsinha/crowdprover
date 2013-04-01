from proveit.programs.models import Program, Invariant, LoopInvariant
from proveit.z3.z3 import *
from proveit.programs.benchmark import *
from proveit.programs.invariantParser import parseInvariant

def substituteFormula(program_id, inv, line):
	program = Program.objects.get(pk=program_id)
	print "boom1"
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)
	states = programStates(z3program)
	print "boom2"
	renamedStates = map((lambda s: s + '_proveit_' + str(line)), states)
	stateVars = map((lambda x : Int(x)), states)
	renamedStateVars = map((lambda x : Int(x)), renamedStates)
	print "boom3"

	print inv
	new_inv = inv
	for i in range(0,len(stateVars)):
		print "boom4"
		new_inv = substitute(new_inv, (stateVars[i], renamedStateVars[i]))
		print new_inv

	print "invariant before substituition: ", inv
	print "invariant after substituition: ", new_inv
	return new_inv

def invariantExistsInDB(invariant, knownInvariants):
	invariantZ3 = parseUserInvariant(invariant)
	for knownInv in knownInvariants:
		knownInvZ3  = parseUserInvariant(knownInv)
		s = Solver()
		equivCheck = And(Implies(invariantZ3, knownInvZ3), Implies(knownInvZ3, invariantZ3))
		s.add(Not(equivCheck))
		if s.check() == unsat:
			return True
	return False
		
def loopinvariantExistsInDB(loopinvariant, knownLoopInvariants):
	loopinvariantZ3 = parseUserInvariant(loopinvariant)
	for knownInv in knownLoopInvariants:
		knownInvZ3  = parseUserInvariant(knownInv)
		s = Solver()
		equivCheck = And(Implies(invariantZ3, knownInvZ3), Implies(knownInvZ3, invariantZ3))
		s.add(Not(equivCheck))
		if s.check() == unsat:
			return True
	return False

def checkInvariant(program_id, knownInvariants, knownLoopInvariants, inv, line):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)

	formula = z3program.programFormula()

	invZ3 = parseUserInvariant(inv)
	ssainv = substituteFormula(program_id, invZ3,line)

	print "Checking user invariant: ", str(ssainv)

	s = Solver()
	#program formula
	s.add(formula)
	#known invariants
	for knownInv in knownInvariants:
		s.add(substituteFormula(program_id, parseUserInvariant(knownInv.content), knownInv.line))
		print "Using known invariant: ", substituteFormula(program_id, parseUserInvariant(knownInv.content), knownInv.line)
	#known loop invariants
	info = z3program.programInfo()
	for knownLoopInv in knownLoopInvariants:
		lastLineOfLoop = info['loops'][knownLoopInv.loopId][1]
		s.add(substituteFormula(program_id, parseUserInvariant(knownLoopInv.content), lastLineOfLoop))
		print "Using known loop invariant: ", substituteFormula(program_id, parseUserInvariant(knownLoopInv.content), lastLineOfLoop)
	#negation of loop conditions
	for loopid in info['loops'].keys():
		lastLineOfLoop = info['loops'][loopid][1]
		loopCond = z3program.loopCondition(loopid)
		s.add(Not(substituteFormula(program_id, loopCond, lastLineOfLoop)))

	#negation of property
	s.add(Not(ssainv))

	if s.check() == unsat:
		print "Proved invariant"
		return (True, 0)
	else:
		print "Unable to prove invariant"
		print s.model()
		return (False, s.model())

def checkLoopInvariant(program_id, knownInvariants, knownLoopInvariants, inv, loop_id):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)
	states = programStates(z3program)
	preStates = map((lambda s: s + '_proveit_pre'), states)
	postStates = map((lambda s: s + '_proveit_post'), states)
	stateVars = map((lambda s : Int(s)), states)
	preStateVars = map((lambda s : Int(s)), preStates)
	postStateVars = map((lambda s : Int(s)), postStates)

	print "Checking user loop invariant on entry: ", str(inv)

	loopEntryLine = loopEntry(z3program, loop_id)
	entryformula = substituteFormula(program_id, parseUserInvariant(inv), loopEntryLine)
	programformula = z3program.programFormula()
	s = Solver()
	#program formula
	s.add(programformula)
	#known invariants
	for knownInv in knownInvariants:
		s.add(substituteFormula(program_id, parseUserInvariant(knownInv.content), knownInv.line))
		print "Using known invariant: ", substituteFormula(program_id, parseUserInvariant(knownInv.content), knownInv.line)
	#known loop invariants
	info = z3program.programInfo()
	for knownLoopInv in knownLoopInvariants:
		lastLineOfLoop = info['loops'][knownLoopInv.loopId][1]
		s.add(substituteFormula(program_id, parseUserInvariant(knownLoopInv.content), lastLineOfLoop))
		print "Using known loop invariant: ", substituteFormula(program_id, parseUserInvariant(knownLoopInv.content), lastLineOfLoop)
	#negation of loop conditions
	for loopid in info['loops'].keys():
		lastLineOfLoop = info['loops'][loopid][1]
		loopCond = z3program.loopCondition(loopid)
		s.add(Not(substituteFormula(program_id, loopCond, lastLineOfLoop)))

	s.add(Not(entryformula))

	if s.check() == sat:
		print "Loop invariant does not hold on entry"
		print s.model()
		return (False, s.model())
	else:
		print "Loop invariant holds on entry. Checking inductively..."


	loopformula = z3program.loopFormula(loop_id) #contains loopCond and transition relation
	precond = parseUserInvariant(inv)
	postcond = parseUserInvariant(inv)
	for i in range(0,len(states)):
		precond = substitute(precond, (stateVars[i], preStateVars[i]))
		postcond = substitute(postcond, (stateVars[i], postStateVars[i]))

	print "Checking user loop invariant inductively: ", str(Implies(precond,postcond))
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
	(succ,obj) = parseInvariant(s)
	print "Z3 object obtained from parsing:",obj

	if succ == 0:
		return obj
	else:
		raise CrowdproverException("Errorcode 1: Could not parse user invariant - "+obj)
