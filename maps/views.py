from lib.web_interface import request_task, create_task_and_maps
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from maps.models import Task, Basemap, Heatmap
# Create your views here.

def request_map(request):
    if request.method == 'POST':
        task = create_task_and_maps(dict(request.POST.items()))
        request_task.delay(task.id)
        return redirect('display_map', task.id)

def display_map(request, task_id):
    if request.method == 'GET':
        task = Task.objects.get(id=task_id)
        data = {
            'task_id': task_id,
            'basemap_id': task.basemap.id,
            'heatmap_id': task.heatmap.id
        }
        return render_to_response('display_map.html', {'data': data})

def task_status(request, task_id):
    if request.method == 'GET':
        task = Task.objects.get(id=task_id)
        if not task.basemap.finished:
            status = task.basemap.status
        else:
            status = 'complete'
        return HttpResponse(u'%s' % status)

def basemap(request, basemap_id):
    if request.method == 'GET':
        basemap = Basemap.objects.get(id=basemap_id)
        if basemap.finished:
            return HttpResponse(u'%s' % basemap.svg_rep)
        else:
            return HttpResponse(u'pending')

def basemap_metadata(request, basemap_id):
    basemap = Basemap.objects.get(id=basemap_id)
    return HttpResponse(basemap.json_metadata(), content_type='application/json')

def heatmap_metadata(request, heatmap_id):
    heatmap = Heatmap.objects.get(id=heatmap_id)
    return HttpResponse(heatmap.json_metadata(), content_type='application/json')

def heatmap(request, heatmap_id):
    if request.method == 'GET':
        heatmap = Heatmap.objects.get(id=heatmap_id)
        if heatmap.finished:
            return HttpResponse(u'%s' % heatmap.terms)
        else:
            return HttpResponse(u'pending')

def query(request):
    if request.method == 'GET':
        return render_to_response('request_map.html', context_instance=RequestContext(request))
