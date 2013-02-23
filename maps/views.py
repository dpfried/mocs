from lib.pipeline import request_task
from django.shortcuts import render_to_response
from django.http import HttpResponse
from maps.models import Task, Basemap, Heatmap
# Create your views here.

def start_request(request):
    if request.method == 'GET':
        # set up new objects
        basemap = Basemap(finished=False)
        basemap.save()
        heatmap = Heatmap(finished=False)
        heatmap.save()
        task = Task(basemap=basemap, heatmap=heatmap)
        task.save()
        sample_size = request.GET['sample_size']
        request = request_task.delay(task.id, sample_size)
        data = {}
        data['task_id'] = task.id
        return render_to_response('request_map.html',
                                  {'data': data})

def task_status(request):
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        task = Task.objects.get(id=task_id)
        if not task.basemap.finished:
            status = task.basemap.status
        else:
            status = task.heatmap.status
        status = task.basemap.status
        return HttpResponse(u'%s' % status)

def map(request):
    if request.method == 'GET':
        task_id = request.GET.get('task_id')
        task = Task.objects.get(id=task_id)
        if task.basemap.finished:
            return HttpResponse(u'%s' % task.basemap.svg_rep)
