from django.http import HttpResponse
from django.template import Context, loader

def index(request):
    template = loader.get_template('index.html')
    context = Context({})
    return HttpResponse(template.render(context))
