from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

import subprocess
import sys
import getopt

from proveit.programs.models import Program, Invariant
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

@dajaxice_register(method='POST')
def suggestInvariant(request, program_id, author, invariant, line):
	print "Hi",author,". You submitted",invariant
	z3Expr = proveit.programs.verifier.parseUserInvariant(invariant)
	(success, model) = proveit.programs.verifier.checkInvariant(program_id, z3Expr, line)
	if success:
		msg = "Correct Invariant: " + invariant
	else:
		msg = "Unable to prove invariant: " + invariant + "\ncex: " + str(model)
	return simplejson.dumps({'message':msg})

@dajaxice_register(method='POST')
def suggestLoopInvariant(request, program_id, author, invariant, line):
	print "Hi",author,". You submitted",invariant
	loop_id = 1 #HARDCODEALERT
	z3Expr = proveit.programs.verifier.parseUserInvariant(invariant)
	(success, model) = proveit.programs.verifier.checkLoopInvariant(program_id, loop_id, z3Expr, line)
	if success:
		msg = "Correct Invariant: " + invariant
	else:
		msg = "Unable to prove invariant: " + invariant + "\ncex: " + str(model)
	return simplejson.dumps({'message':msg})

