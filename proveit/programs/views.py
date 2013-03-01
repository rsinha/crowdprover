from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

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
        code = open(program.source, 'r').read()
	trace = [{'alias': 'x', 'values': ['1', '2', '3', '4', '5', '6', '7', '8', '9'], 'name': 'x'}, {'alias': 'n_data', 'values': ['1', '2', '3', '4', '5', '6', '7', '8', '9'], 'name': 'n->data'},{'alias': 'n_next', 'values': ["0xabcd", "0xabcd", "0xbacd", "0xbeee", "0xabcd", "0xbecf", "0xbcef", "0xabcd", "0xdead", "0xabcd", "0xabcd", "0xabcd"], 'name': 'n->next'}]
    except Program.DoesNotExist:
        raise Http404
    return render(request, 'programs/detail.html', {'program': program, 'code': code, 'trace':trace})

def results(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    code = open(program.source, 'r').read() 
    return render(request, 'programs/results.html', {'program': program, 'code': code})

def submit(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    code = open(program.source, 'r').read() 
    trace = [{'alias': 'x', 'values': ['1', '2', '3', '4', '5', '6', '7', '8', '9'], 'name': 'x'}, {'alias': 'n_data', 'values': ['1', '2', '3', '4', '5', '6', '7', '8', '9'], 'name': 'n->data'},{'alias': 'n_next', 'values': ["0xabcd", "0xabcd", "0xbacd", "0xbeee", "0xabcd", "0xbecf", "0xbcef", "0xabcd", "0xdead", "0xabcd", "0xabcd", "0xabcd"], 'name': 'n->next'}]
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
