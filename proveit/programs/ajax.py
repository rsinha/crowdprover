from django.utils import simplejson, timezone
from dajaxice.decorators import dajaxice_register

import subprocess
import sys
import getopt

from proveit.programs.models import Program, Invariant, LoopInvariant
import proveit.programs.proveutils
import proveit.programs.verifier

#TODO: parse errors result in code 3, implement graceful response to parse errors

@dajaxice_register(method='GET')
def computeTrace(request, program_id, inputs):
	print inputs
	program = Program.objects.get(pk=program_id)
	print "program id: ", program_id
	trace = proveit.programs.proveutils.computeTrace(proveit.programs.proveutils.absoluteMeta(program.source),proveit.programs.proveutils.absoluteBinary(program.binary), inputs) 
	print "success"
	return simplejson.dumps(trace)

@dajaxice_register(method='POST')
def suggestInvariant(request, program_id, author, invariant, line):
	print author," submitted ",invariant," as an invariant for line ", line
	program = Program.objects.get(pk=program_id)
	date = timezone.now()

	print "boom1"
	if not(proveit.programs.verifier.parseableInvariant(program, invariant)):
		print "boom2"
		msg = "Could not parse your invariant"
		response = {}
		response['code'] = 3 #denotes parse error
		response['invariant'] = invariant
		response['author'] = author
		response['content'] = msg
		return simplejson.dumps(response)
	print "boom3"

	(exists, existingInv) = proveit.programs.verifier.invariantExistsInDB(program_id, invariant, int(line))
	if exists:
		msg = existingInv.author + " already submitted an equivalent invariant: " + str(existingInv)
		response = {}
		response['code'] = 4 #denotes duplicate submission
		response['invariant'] = str(existingInv)
		response['author'] = str(existingInv.author)
		response['content'] = msg
		return simplejson.dumps(response)

	(success, model) = proveit.programs.verifier.checkInvariant(program_id, invariant, int(line))
	response = {}
	response['invariant'] = invariant
	response['author'] = author
	if success == 1:
		response['code'] = 1
		response['content'] = "Able to prove invariant: " + invariant + " correct"
	elif success == 2:
		response['code'] = 2
		response['content'] = "Able to prove invariant: " + invariant + " incorrect"
	elif success == 0:
		response['code'] = 0
		response['content'] = "Unable to prove invariant: " + invariant
		response['cex'] = str(model) #TODO: Fix this
	print "Adding invariant", invariant, "to DB..."
	program.invariant_set.create(author=author, content=invariant, line=int(line), date=date,status=success)

	if success == 1:
		#The suggested inv may end up proving previously suggested inv
		#try proving the unknown invariants now
		proveit.programs.verifier.proveUnknownInvariants(program_id)
		#try proving the program now
		proveit.programs.verifier.proveProgram(program_id)

	return simplejson.dumps(response)

@dajaxice_register(method='POST')
def suggestLoopInvariant(request, program_id, author, invariant, loop_id):
	print author," submitted ",invariant," as a loop invariant for loop id ", loop_id
	program = Program.objects.get(pk=program_id)
	date = timezone.now()

	if not proveit.programs.verifier.parseableInvariant(program, invariant):
		msg = "Could not parse your invariant"
		response = {}
		response['code'] = 3 #denotes parse error
		response['invariant'] = invariant
		response['author'] = author
		response['content'] = msg
		return simplejson.dumps(response)


	(exists, existingInv) = proveit.programs.verifier.loopinvariantExistsInDB(program_id, invariant, int(loop_id))
	if exists:
		msg = existingInv.author + " already submitted an equivalent loop invariant" + str(existingInv)
		response = {}
		response['code'] = 4 #denotes duplicate submission
		response['invariant'] = str(existingInv)
		response['author'] = str(existingInv.author)
		response['content'] = msg
		return simplejson.dumps(response)

	(success, model) = proveit.programs.verifier.checkLoopInvariant(program_id, invariant, int(loop_id))
	response = {}
	response['invariant'] = invariant
	response['author'] = author
	if success == 1:
		response['code'] = 1
		response['content'] = "Able to prove loop invariant: " + invariant + " correct"
	if success == 2:
		response['code'] = 2
		response['content'] = "Able to prove loop invariant: " + invariant + " incorrect"
	elif success == 0:
		response['code'] = 0
		response['content'] = "Unable to prove loop invariant: " + invariant
		response['cex'] = str(model) #TODO: Fix this
	print "Adding loop invariant", invariant, "to DB..."
	program.loopinvariant_set.create(author=author, content=invariant, loopId=int(loop_id), date=date,status=success)

	if success == 1:
		#The suggested inv may end up proving previously suggested inv
		#try proving the unknown invariants now
		proveit.programs.verifier.proveUnknownInvariants(program_id)
		#try proving the program now
		proveit.programs.verifier.proveProgram(program_id)

	return simplejson.dumps(response)

