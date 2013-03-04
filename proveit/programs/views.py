from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render
from django.utils import timezone
import subprocess
import sys
import getopt

from proveit.programs.models import Program, Invariant

def index(request):
    program_list = Program.objects.all()
    context = Context({
        'program_list': program_list,
    })
    return render(request, 'programs/index.html', context)

def detail(request, program_id):
    try:
        program = Program.objects.get(pk=program_id)
        code = open(absoluteSource(program.source), 'r').read()
	trace = computeTrace(absoluteBinary(program.binary), [11]) #HARDCODEALERT
    except Program.DoesNotExist:
        raise Http404
    return render(request, 'programs/detail.html', {'program': program, 'code': code, 'trace':trace})

def results(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    code = open(absoluteSource(program.source), 'r').read() 
    return render(request, 'programs/results.html', {'program': program, 'code': code})

#think about using cookies here to save the last trace
def submit(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    code = open(absoluteSource(program.source), 'r').read()
    trace = computeTrace(absoluteBinary(program.binary), [11]) #HARDCODEALERT
    author = request.POST['author']
    content = request.POST['content']
    line = request.POST['line']
    date = timezone.now()
    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    #return HttpResponseRedirect(reverse('programs:results', args=(program.id,)))
    if author == "" or content == "" or line == "": 
        # Redisplay the program voting form.
        return render(request, 'programs/detail.html', {
            'program': program,
	    'code': code,
	    'trace': trace,
            'error_message': "Please fill all fields.",
        })
    else:
        program.invariant_set.create(author=author, content=content, line=int(line), date=date)
        return render(request, 'programs/results.html', {'program': program, 'code': code})

def computeTrace(binary,inputs):
	absolute_binary = "proveit/bin/" + binary
	procOptions = [absolute_binary]
	for inp in inputs:
		procOptions += str(inp)
        proc = subprocess.Popen(procOptions,stdout=subprocess.PIPE)
        trace = {}
        loopCounter = 0 
        while True:
                line = proc.stdout.readline()
                if line != '': 
                        elements = line.split(',')
                        if loopCounter == 0:
                                trace['length'] = 0 
                                trace['values'] = []
                                for element in elements:
                                        element_t = element.split(':')[0]
                                        element_v = element.split(':')[1]
                                        if element_t == "line":
                                                trace['firstLine'] = int(element_v)
                                                trace['lines'] = [element_v]
                                        else:
                                                trace['values'] += [{'name':element_t, 'values':[element_v.rstrip()], 'alias': nameToAlias(element_t)}]
                        else:
                                for element in elements:
                                        element_t = element.split(':')[0]
                                        element_v = element.split(':')[1]
                                        if element_t == "line":
                                                trace['lines'] += [element_v]
                                        else:
                                                for var in trace['values']:
                                                        if var['name'] == element_t:
                                                                var['values'] += [element_v.rstrip()]
                                                                break
      
      
                        print line.rstrip()
                        trace['length'] += 1
                        loopCounter = loopCounter + 1 
                else:
                        break
        return trace

def nameToAlias(name):
	return '_'.join(name.split('->'))

def absoluteBinary(binary):
	return "proveit/bin/" + binary

def absoluteSource(source):
	return "proveit/programs/static/code/" + source

