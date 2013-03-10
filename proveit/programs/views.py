from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
import subprocess
import sys
import getopt

from proveit.programs.models import Program, Invariant
import proveit.programs.proveutils

def index(request):
    program_list = Program.objects.all()
    context = Context({
        'program_list': program_list,
    })
    return render(request, 'programs/index.html', context)

def detail(request, program_id):
    try:
        program = Program.objects.get(pk=program_id)
	print "program id: ", program_id
	code = open(proveit.programs.proveutils.absoluteSource(program.source), 'r').read()
	meta = open(proveit.programs.proveutils.absoluteMeta(program.source), 'r').readlines()
	inputs = []
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
		inputs += [int(vardefault)]
	trace = proveit.programs.proveutils.computeTrace(proveit.programs.proveutils.absoluteMeta(program.source), proveit.programs.proveutils.absoluteBinary(program.binary), inputs) 
    except Program.DoesNotExist:
        raise Http404
    return render(request, 'programs/detail.html', {'program': program, 'code': code, 'trace':trace})

def results(request, program_id):
	program = get_object_or_404(Program, pk=program_id)
	code = open(proveit.programs.proveutils.absoluteMeta(program.source), proveit.programs.proveutils.absoluteSource(program.source), 'r').read() 
	return render(request, 'programs/results.html', {'program': program, 'code': code})

#think about using cookies here to save the last trace
def submit(request, program_id):
	program = get_object_or_404(Program, pk=program_id)
	code = open(proveit.programs.proveutils.absoluteSource(program.source), 'r').read()
	meta = open(proveit.programs.proveutils.absoluteMeta(program.source), 'r').readlines()
	inputs = []
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
        	inputs += [int(vardefault)]
    	trace = proveit.programs.proveutils.computeTrace(proveit.programs.proveutils.absoluteMeta(program.source), proveit.programs.proveutils.absoluteBinary(program.binary), inputs) 
	author = request.POST['author']
	content = request.POST['content']
	line = request.POST['line']
	date = timezone.now()
    	if author == "" or content == "" or line == "": 
        	return render(request, 'programs/detail.html', {
            	'program': program,
	    	'code': code,
	    	'trace': trace,
            	'error_message': "Please fill all fields.",
        	})
    	else:
        	program.invariant_set.create(author=author, content=content, line=int(line), date=date)
        	return render(request, 'programs/results.html', {'program': program, 'code': code})

