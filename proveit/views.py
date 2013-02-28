from django.http import HttpResponse

def index(request):
    return HttpResponse("<html><body>You are at the main page. Check out our <a href="/programs">programs</a></body></html>")
