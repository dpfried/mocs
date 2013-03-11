from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import commands

@login_required
def reload_site(request):#, login_url=reverse('admin:index')):
    pid = commands.restart_django()
    return HttpResponse(u'killed process %s' % pid, content_type='text/plain')

@login_required
def restart_celery(request):
    old_pid, new_pid = commands.restart_celery()
    return HttpResponse('old pid: %s\nnew pid: %s' % (old_pid, new_pid), content_type='text/plain')

@login_required
def syncdb(request):
    output = commands.syncdb()
    return HttpResponse(output, content_type='text/plain')

def home(request):
    return HttpResponse(u'Django is working.')
