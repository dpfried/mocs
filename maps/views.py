from lib.web_interface import request_task, request_heatmap, create_task_and_maps, create_task_with_existing_basemap
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse
from maps.models import Task, Basemap, Heatmap
from lib.pipeline import call_graphviz
# Create your views here.

def request_map(request):
    if request.method == 'POST':
        include_heatmap = 'draw_heatmap' in request.POST
        use_existing_basemap = 'use_existing_basemap' in request.POST
        if use_existing_basemap:
            basemap_id = Task.objects.get(id=request.POST['existing_task_id']).basemap.id
            task = create_task_with_existing_basemap(basemap_id, dict(request.POST.items()))
            request_heatmap.delay(task.id)
        else:
            task = create_task_and_maps(dict(request.POST.items()), include_heatmap=include_heatmap)
            request_task.delay(task.id)
        return redirect('display_map', task.id)

def display_map(request, task_id):
    if request.method == 'GET':
        task = Task.objects.get(id=task_id)
        data = {
            'task_id': task_id,
            'basemap_id': task.basemap.id,
            'heatmap_id': task.heatmap.id if task.heatmap is not None else -1
        }
        return render_to_response('maps/display_map.html', {'data': data})

def task_status(request, task_id):
    if request.method == 'GET':
        task = Task.objects.get(id=task_id)
        if not task.basemap.finished:
            status = task.basemap.status
        else:
            status = 'complete'
        return HttpResponse(u'%s' % status)

MIME_TYPES = {
    'pdf': 'application/pdf',
    'png': 'image/png',
    'jpg': 'image/jpeg',
    'gif': 'image/gif',
    'svg': 'image/svg+xml',
}

def basemap(request, basemap_id):
    if request.method == 'GET':
        basemap = Basemap.objects.get(id=basemap_id)
        if 'ft' in request.GET:
            ft = request.GET['ft']
            if ft in MIME_TYPES:
                output = call_graphviz(basemap.dot_rep, file_format=ft, model=basemap)
                return HttpResponse(output, content_type=MIME_TYPES[ft])
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

def heatmap_for_task_id(request, task_id):
    return heatmap(request, Task.objects.get(id=task_id).heatmap.id)

def basemap_for_task_id(request, task_id):
    return basemap(request, Task.objects.get(id=task_id).basemap.id)

def query(request):
    if request.method == 'GET':
        return render_to_response('maps/request_map.html', context_instance=RequestContext(request))

def dev_query(request):
    if request.method == 'GET':
        return render_to_response('maps/request_map_dev.html', context_instance=RequestContext(request))

def new_query(request):
    return render_to_response('maps/request_map_new.html', context_instance=RequestContext(request))
