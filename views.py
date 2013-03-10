from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from restart import restart

@login_required
def reload_site(request):#, login_url=reverse('admin:index')):
    pid = restart()
    return HttpResponse(u'killed process %s' % pid)

def home(request):
    return HttpResponse(u'Django is working.')
