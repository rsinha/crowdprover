from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

import subprocess
import sys
import getopt

from proveit.programs.models import Program, Invariant
import proveit.programs.proveutils

@dajaxice_register(method='GET')
def sayhello1(request, program_id, inputs):
	print inputs
	program = Program.objects.get(pk=program_id)
	print "program id: ", program_id
	trace = proveit.programs.proveutils.computeTrace(proveit.programs.proveutils.absoluteMeta(program.source),proveit.programs.proveutils.absoluteBinary(program.binary), inputs) 
	print "success"
	return simplejson.dumps(trace)

@dajaxice_register(method='POST')
def invariantToServer(request, program_id, author, invariant, line):
	print "Hi",author,". You submitted",invariant
	msg = "Hello"+author+" "+invariant
	return simplejson.dumps({'message':msg})
