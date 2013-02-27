from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import Context, loader
from django.shortcuts import get_object_or_404, render

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
    except Program.DoesNotExist:
        raise Http404
    return render(request, 'programs/detail.html', {'program': program, 'code': code})


def results(request, program_id):
    program = get_object_or_404(Program, pk=program_id)
    return render(request, 'programs/results.html', {'program': program})

def annotate(request, program_id):
    p = get_object_or_404(Program, pk=program_id)
    try:
        content = request.POST['content']
        line = request.POST['line']
        author = request.POST['author']
        date = request.POST['date']
    except (KeyError, Invariant.DoesNotExist):
        # Redisplay the program voting form.
        return render(request, 'programs/detail.html', {
            'program': p,
            'error_message': "Please enter all fields before submitting.",
        })
    else:
        #selected_choice.votes += 1
        #selected_choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('programs:results', args=(p.id,)))
