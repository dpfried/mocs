from django.db import models

# Create your models here.
class Basemap(models.Model):
    dot_rep = models.TextField()
    svg_rep = models.TextField()
    finished = models.BooleanField()
    status = models.TextField()

class Heatmap(models.Model):
    terms = models.TextField()
    finished = models.BooleanField()
    status = models.TextField()

class Task(models.Model):
    basemap = models.ForeignKey(Basemap)
    heatmap = models.ForeignKey(Heatmap)

def create_task_and_maps():
    # set up new objects
    basemap = Basemap(finished=False)
    basemap.save()
    heatmap = Heatmap(finished=False)
    heatmap.save()
    task = Task(basemap=basemap, heatmap=heatmap)
    task.save()
    return task
