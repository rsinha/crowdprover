from django.utils import simplejson, timezone
from dajaxice.decorators import dajaxice_register

import subprocess
import sys
import getopt

from proveit.programs.models import Program, Invariant, LoopInvariant
import proveit.programs.proveutils
import proveit.programs.verifier

@dajaxice_register(method='GET')
def computeTrace(request, program_id, inputs):
	print inputs
	program = Program.objects.get(pk=program_id)
	print "program id: ", program_id
	trace = proveit.programs.proveutils.computeTrace(proveit.programs.proveutils.absoluteMeta(program.source),proveit.programs.proveutils.absoluteBinary(program.binary), inputs) 
	print "success"
	return simplejson.dumps(trace)

@dajaxice_register(method='GET')
def suggestInvariant(request, program_id, author, invariant, line):
	print author," submitted ",invariant," as an invariant for line ", line
	program = Program.objects.get(pk=program_id)
	date = timezone.now()

	(exists, existingInv) = proveit.programs.verifier.invariantExistsInDB(program_id, invariant, int(line))
	if exists:
		msg = existingInv.author + " already submitted " + invariant +" as an invariant"
		return simplejson.dumps({'message':msg})

	(success, model) = proveit.programs.verifier.checkInvariant(program_id, invariant, int(line))
	msg = ""
	if success == 1:
		msg = "Able to prove invariant: " + invariant + " correct"
	elif success == 2:
		msg = "Able to prove invariant: " + invariant + " incorrect"
	elif success == 0:
		msg = "Unable to prove invariant: " + invariant + "\ncex: " + str(model)
	print "Adding invariant", invariant, "to DB..."
	program.invariant_set.create(author=author, content=invariant, line=int(line), date=date,status=success)

	if success == 1:
		#The suggested inv may end up proving previously suggested inv
		#try proving the unknown invariants now
		proveit.programs.verifier.proveUnknownInvariants(program_id)
		#try proving the program now
		proveit.programs.verifier.proveProgram(program_id)

	return simplejson.dumps({'message':msg})

@dajaxice_register(method='GET')
def suggestLoopInvariant(request, program_id, author, invariant, loop_id):
	print author," submitted ",invariant," as a loop invariant for loop id ", loop_id
	program = Program.objects.get(pk=program_id)
	date = timezone.now()
	(exists, existingInv) = proveit.programs.verifier.loopinvariantExistsInDB(program_id, invariant, int(loop_id))
	if exists:
		msg = existingInv.author + " already submitted " + invariant +" as a loop invariant"
		return simplejson.dumps({'message':msg})

	(success, model) = proveit.programs.verifier.checkLoopInvariant(program_id, invariant, int(loop_id))
	msg = ""
	if success == 1:
		msg = "Able to prove loop invariant: " + invariant + " correct"
	if success == 2:
		msg = "Able to prove loop invariant: " + invariant + " incorrect"
	elif success == 0:
		msg = "Unable to prove loop invariant: " + invariant + "\ncex: " + str(model)
	print "Adding loop invariant", invariant, "to DB..."
	program.loopinvariant_set.create(author=author, content=invariant, loopId=int(loop_id), date=date,status=success)

	if success == 1:
		#The suggested inv may end up proving previously suggested inv
		#try proving the unknown invariants now
		proveit.programs.verifier.proveUnknownInvariants(program_id)
		#try proving the program now
		proveit.programs.verifier.proveProgram(program_id)
		#try proving the program now

	return simplejson.dumps({'message':msg})

