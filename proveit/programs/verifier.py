from django.utils import timezone
from proveit.programs.models import Program, Invariant, LoopInvariant
from proveit.z3.z3 import *
from proveit.programs.benchmark import *
from proveit.programs.invariantParser import parseInvariant
import proveit.programs.proveutils

def substituteFormula(program_id, inv, line):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)
	states = programStates(z3program)
	renamedStates = map((lambda s: s + '_proveit_' + str(line)), states)
	stateVars = map((lambda x : Int(x)), states)
	renamedStateVars = map((lambda x : Int(x)), renamedStates)

	new_inv = inv
	for i in range(0,len(stateVars)):
		new_inv = substitute(new_inv, (stateVars[i], renamedStateVars[i]))

	return new_inv

def parseableInvariant(program, invariant):
	(succ,obj) = parseInvariant(invariant,program.description)
	return (succ == 0)

def invariantExistsInDB(program_id, invariant, line):
	print "Checking existence of suggested invariant within DB..."
	program = Program.objects.get(pk=program_id)
	knownInvariants = program.invariant_set.all()
	invariantZ3 = parseUserInvariant(invariant, program.description)
	for knownInv in knownInvariants:
		if knownInv.line != line:
			continue
		knownInvZ3  = parseUserInvariant(knownInv.content, program.description)
		s = Solver()
		equivCheck = And(Implies(invariantZ3, knownInvZ3), Implies(knownInvZ3, invariantZ3))
		s.add(Not(equivCheck))
		if s.check() == unsat:
			print "Suggested invariant found within DB..."
			return (True, knownInv)
	print "Suggested invariant not found within DB..."
	return (False, 0)
		
def loopinvariantExistsInDB(program_id, loopinvariant, loopId):
	print "Checking existence of suggested loop invariant within DB..."
	program = Program.objects.get(pk=program_id)
	knownLoopInvariants = program.loopinvariant_set.all()
	loopinvariantZ3 = parseUserInvariant(loopinvariant, program.description)
	for knownInv in knownLoopInvariants:
		if knownInv.loopId != loopId:
			continue
		knownInvZ3  = parseUserInvariant(knownInv.content, program.description)
		s = Solver()
		equivCheck = And(Implies(loopinvariantZ3, knownInvZ3), Implies(knownInvZ3, loopinvariantZ3))
		s.add(Not(equivCheck))
		if s.check() == unsat:
			print "Suggested loop invariant found within DB..."
			return (True, knownInv)
	print "Suggested loop invariant not found within DB..."
	return (False, 0)

def proveProgram(program_id):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)

	assertions = z3program.programAsserts()
	for assertion in assertions:
		(success,model) = checkInvariant(program_id, assertion[1], assertion[0])
		if success == 0:
			return

	program.status = 1
	program.save()
	return

def proveUnknownInvariants(program_id):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)
	info = z3program.programInfo()
	unknownInvariants = filter((lambda inv: inv.status == 0), program.invariant_set.all())
	unknownLoopInvariants = filter((lambda inv: inv.status == 0), program.loopinvariant_set.all())

	for unknownInv in unknownInvariants:
		(success,model) = checkInvariant(program_id, unknownInv.content, unknownInv.line)
		if success == 1:
			unknownInv.status = 1
			unknownInv.save()
	for unknownLoopInv in unknownLoopInvariants:
		(success,model) = checkLoopInvariant(program_id, unknownLoopInv.content, unknownLoopInv.loopId)
		if success:
			unknownLoopInv.status = 1
			unknownLoopInv.save()
"""	
	for loopid in info['loops'].keys():
		print "loopid: ", loopid
		submittedLoopInvariants = filter((lambda inv: inv.loopId == loopid), program.loopinvariant_set.all())
		combinedAuthor = lambda x : lambda y: x if x in y else (y if y in x else (x + ',' + y))
		candidates = []
		candidates += [('('+x.content+')' + ' & ' + '('+y.content+')', combinedAuthor(x.author)(y.author)) for x in submittedLoopInvariants for y in submittedLoopInvariants if x != y]
		candidates += [('('+x.content+')' + ' | ' + '('+y.content+')', combinedAuthor(x.author)(y.author)) for x in submittedLoopInvariants for y in submittedLoopInvariants if x != y]
		print "candidates: ", candidates
		for candidate in candidates:
			(exists, existingInv) = loopinvariantExistsInDB(program_id, candidate[0], loopid)
			if exists:
				continue
			(success,model) = checkLoopInvariant(program_id, candidate[0], loopid)
			if success:
				date = timezone.now()
				program.loopinvariant_set.create(author=candidate[1], content=candidate[0], loopId=loopid, date=date,status=1)
"""
	return

def modelToLoopCex(program_id, loop_id, model):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)
	info = z3program.programInfo()
	meta = proveit.programs.proveutils.absoluteMeta(program.source)
	binary = proveit.programs.proveutils.absoluteBinary(program.binary)


	trace = {}
	trace['inputs'] = []
	meta = open(meta, 'r').readlines()
	for line in meta:
		elements = line.rstrip().split(',')
		varname = ""
		vardefault = ""
		for element in elements:
			element_t = element.split(':')[0]
			element_v = element.split(':')[1]
			if element_t == 'name':
				varname = element_v
			elif element_t == 'default':
				vardefault = element_v
		trace['inputs'] += [{'name':varname, 'default':vardefault}]

	values = {}
	trace['length'] = 2 #pre n post
	trace['lines'] = [info['loops'][loop_id][0], info['loops'][loop_id][1]]
	trace['values'] = []
	for state in info['states'].keys():
		values[state] = []
		z3Var = Int(state + '_proveit_pre')
		z3Interp = model[z3Var]
		if str(z3Interp) == 'None':
			values[state] += ['-']
		else:
			values[state] += [str(z3Interp)]
	for state in info['states'].keys():
		z3Var = Int(state + '_proveit_post')
		z3Interp = model[z3Var]
		if str(z3Interp) == 'None':
			values[state] += ['-']
		else:
			values[state] += [str(z3Interp)]

	trace['firstLine'] = info['loops'][loop_id][0]
	for state in info['states'].keys():
		trace['values'] += [{'name': state, 'values':values[state]}]

	inputs = {}
	inputs['names'] = []
	inputs['values'] = []
	inputs['length'] = len(info['inputs'].keys())
	for input in info['inputs'].keys():
		z3Var = Int(input)
		z3Interp = model[z3Var]
		if str(z3Interp) == 'None':
			inputs['names'] += [input]
			inputs['values'] += ['-']
		else:
			inputs['names'] += [input]
			inputs['values'] += [str(z3Interp)]
	trace['inputs'] = inputs
	return trace

def modelToCex(program_id, model):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)
	info = z3program.programInfo()
	meta = proveit.programs.proveutils.absoluteMeta(program.source)
	binary = proveit.programs.proveutils.absoluteBinary(program.binary)

	trace = {}
	trace['inputs'] = []
	meta = open(meta, 'r').readlines()
	for line in meta:
		elements = line.rstrip().split(',')
		varname = ""
		vardefault = ""
		for element in elements:
			element_t = element.split(':')[0]
			element_v = element.split(':')[1]
			if element_t == 'name':
				varname = element_v
			elif element_t == 'default':
				vardefault = element_v
		trace['inputs'] += [{'name':varname, 'default':vardefault}]

	firstLinehit = False
	values = {}
	trace['length'] = 0
	trace['lines'] = []
	trace['values'] = []
	for state in info['states'].keys():
		values[state] = []
	for line in range(info['codelines'][0],info['codelines'][1]):
		skipThisLine = True
		for state in info['states'].keys():
			z3Var = Int(state + '_proveit_' + str(line))
			z3Interp = model[z3Var]
			if str(z3Interp) != 'None':
				skipThisLine = False
		if (skipThisLine):
			continue
		trace['lines'] += [line]
		trace['length'] += 1
		for state in info['states'].keys():
			z3Var = Int(state + '_proveit_' + str(line))
			z3Interp = model[z3Var]
			if str(z3Interp) == 'None':
				values[state] += ['-']
			else:
				values[state] += [str(z3Interp)]
			
	trace['firstLine'] = min(trace['lines'])
	for state in info['states'].keys():
		trace['values'] += [{'name': state, 'values':values[state]}]

	inputs = {}
	inputs['names'] = []
	inputs['values'] = []
	inputs['length'] = len(info['inputs'].keys())
	for input in info['inputs'].keys():
		z3Var = Int(input)
		z3Interp = model[z3Var]
		if str(z3Interp) == 'None':
			inputs['names'] += [input]
			inputs['values'] += ['-']
		else:
			inputs['names'] += [input]
			inputs['values'] += [str(z3Interp)]
	trace['inputs'] = inputs	

	return trace

def checkInvariant(program_id, inv, line):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)

	formula = z3program.programFormula()

	invZ3 = parseUserInvariant(inv, program.description)
	ssainv = substituteFormula(program_id, invZ3,line)

	print "Checking user invariant: ", str(ssainv)

	knownInvariants = filter((lambda inv: inv.status == 1), program.invariant_set.all())
	knownLoopInvariants = filter((lambda inv: inv.status == 1), program.loopinvariant_set.all())

	s = Solver()
	#program formula
	s.add(formula)
	#known invariants
	for knownInv in knownInvariants:
		s.add(substituteFormula(program_id, parseUserInvariant(knownInv.content, program.description), knownInv.line))
		print "Using known invariant: ", substituteFormula(program_id, parseUserInvariant(knownInv.content, program.description), knownInv.line)
	#known loop invariants
	info = z3program.programInfo()
	for knownLoopInv in knownLoopInvariants:
		lastLineOfLoop = loopExit(z3program, knownLoopInv.loopId)
		firstLineOfLoop = loopEntry(z3program, knownLoopInv.loopId)
		s.add(substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), lastLineOfLoop))
		s.add(substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), firstLineOfLoop))
		#print "Using known loop invariant: ", substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), lastLineOfLoop)
		#print "Using known loop invariant: ", substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), firstLineOfLoop)
	#negation of loop conditions
	for loopid in info['loops'].keys():
		lastLineOfLoop = loopExit(z3program, loopid)
		loopCond = z3program.loopCondition(loopid)
		#print "Using negated loop condition", Not(substituteFormula(program_id, loopCond, lastLineOfLoop))
		s.add(Not(substituteFormula(program_id, loopCond, lastLineOfLoop)))

	#First check for No (in all executions)
	s.push()
	s.add(ssainv)
	if s.check() == unsat:
		print "Proved invariant false"
		return (2, 0)
	s.pop()

	s.push()
	#negation of property
	s.add(Not(ssainv))

	if s.check() == unsat:
		print "Proved invariant"
		return (1, 0)
	else:
		print "Unable to prove invariant"
		return (0, modelToCex(program_id, s.model()))

def checkLoopInvariant(program_id, inv, loop_id):
	program = Program.objects.get(pk=program_id)
	factory = Z3ProgramFactory()
	z3program = factory.newProgram(program.description)
	states = programStates(z3program)
	preStates = map((lambda s: s + '_proveit_pre'), states)
	postStates = map((lambda s: s + '_proveit_post'), states)
	stateVars = map((lambda s : Int(s)), states)
	preStateVars = map((lambda s : Int(s)), preStates)
	postStateVars = map((lambda s : Int(s)), postStates)

	knownInvariants = filter((lambda inv: inv.status == 1), program.invariant_set.all())
	knownLoopInvariants = filter((lambda inv: inv.status == 1), program.loopinvariant_set.all())

	print "Checking user loop invariant on entry: ", inv

	loopEntryLine = loopEntry(z3program, loop_id)
	entryformula = substituteFormula(program_id, parseUserInvariant(inv, program.description), loopEntryLine)
	programformula = z3program.programFormula()
	s = Solver()
	#program formula
	s.add(programformula)
	#known invariants
	for knownInv in knownInvariants:
		s.add(substituteFormula(program_id, parseUserInvariant(knownInv.content, program.description), knownInv.line))
		#print "Using known invariant: ", substituteFormula(program_id, parseUserInvariant(knownInv.content, program.description), knownInv.line)
	#known loop invariants
	info = z3program.programInfo()
	for knownLoopInv in knownLoopInvariants:
		lastLineOfLoop = loopExit(z3program, knownLoopInv.loopId)
		firstLineOfLoop = loopEntry(z3program, knownLoopInv.loopId)
		s.add(substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), lastLineOfLoop))
		s.add(substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), firstLineOfLoop))
		#print "Using known loop invariant: ", substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), lastLineOfLoop)
		#print "Using known loop invariant: ", substituteFormula(program_id, parseUserInvariant(knownLoopInv.content, program.description), firstLineOfLoop)
	#negation of loop conditions
	for loopid in info['loops'].keys():
		lastLineOfLoop = loopExit(z3program, loopid)
		loopCond = z3program.loopCondition(loopid)
		#print "Using negated loop condition", Not(substituteFormula(program_id, loopCond, lastLineOfLoop))
		s.add(Not(substituteFormula(program_id, loopCond, lastLineOfLoop)))

	#First check for No (in all executions)
	s.push()
	s.add(entryformula)
	if s.check() == unsat:
		print "Proved loop invariant false"
		return (2, 0)
	s.pop()

	s.push()
	s.add(Not(entryformula))

	if s.check() == sat:
		print "Loop invariant does not hold on entry"
		return (0, modelToCex(program_id, s.model()))
	else:
		print "Loop invariant holds on entry. Checking inductively..."




	print "Checking user loop invariant inductively: ", inv

	s = Solver()
	
	loopformula = z3program.loopFormula(loop_id) #contains loopCond and transition relation
	s.add(loopformula)

	for knownLoopInv in knownLoopInvariants:
		precond = parseUserInvariant(knownLoopInv.content, program.description)
		for i in range(0,len(states)):
			precond = substitute(precond, (stateVars[i], preStateVars[i]))
		s.add(precond)

	precond = parseUserInvariant(inv, program.description)
	postcond = parseUserInvariant(inv, program.description)
	for i in range(0,len(states)):
		precond = substitute(precond, (stateVars[i], preStateVars[i]))
		postcond = substitute(postcond, (stateVars[i], postStateVars[i]))
	s.add(Not(Implies(precond, postcond)))

	if s.check() == unsat:
		print "Proved loop invariant"
		return (1, 0)
	else:
		print "Unable to prove loop invariant"
		return (0, modelToLoopCex(program_id, loop_id, s.model()))

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

def loopExit(z3program, loop_id):
	info = z3program.programInfo()
	loops = info['loops']
	return loops[loop_id][1]

def parseUserInvariant(s,description):
	(succ,obj) = parseInvariant(s,description)

	if succ == 0:
		return obj
	else:
		raise CrowdproverException("Errorcode 1: Could not parse user invariant - "+obj)
