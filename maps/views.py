from lib.pipeline import request_task, map_args
from django.shortcuts import render_to_response
from django.http import HttpResponse
from maps.models import Task, create_task_and_maps
# Create your views here.

def start_request(request):
    task = create_task_and_maps()
    request_task.delay(task.id, **map_args(request.GET))
    return task.id

def get_task(request):
    if request.method == 'GET':
        if 'task_id' in request.GET:
            try:
                task_id = int(request.GET['task_id'])
                # check if the task exists, will raise DoesNotExist if it doesn't
                Task.objects.get(id=task_id)
            except (ValueError, Task.DoesNotExist):
                task_id = start_request(request)
        else:
            task_id = start_request(request)
        data = {
            'task_id': task_id,
        }
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
