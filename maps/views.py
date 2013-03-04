from lib.pipeline import request_task
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from maps.models import Task, create_task_and_maps
# Create your views here.

def request_map(request):
    if request.method == 'POST':
        task = create_task_and_maps()
        request_task.delay(task.id, **dict(request.POST.items()))
        return redirect('display_map', task.id)

def display_map(request, task_id):
    if request.method == 'GET':
        Task.objects.get(id=task_id)
        data = {
            'task_id': task_id,
        }
        return render_to_response('display_map.html', {'data': data})

def task_status(request):
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        task = Task.objects.get(id=task_id)
        if not task.basemap.finished:
            status = task.basemap.status
        else:
            status = 'complete'
        return HttpResponse(u'%s' % status)

def basemap(request, task_id):
    if request.method == 'GET':
        task = Task.objects.get(id=task_id)
        if task.basemap.finished:
            return HttpResponse(u'%s' % task.basemap.svg_rep)

def heatmap(request):
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        task = Task.objects.get(id=task_id)
        if task.heatmap.finished:
            return HttpResponse(u'%s' % task.heatmap.terms)

def query(request):
    if request.method == 'GET':
        return render_to_response('request_map.html', context_instance=RequestContext(request))
