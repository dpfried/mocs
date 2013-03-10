from django.db import models
from json import dumps

# Create your models here.
class Basemap(models.Model):
    dot_rep = models.TextField()
    svg_rep = models.TextField()
    finished = models.BooleanField()
    status = models.TextField()
    height = models.FloatField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)

    def metadata(self):
        return {
            'status': self.status,
            'height': self.height,
            'width': self.width,
            'finished': self.finished
        }

    def json_metadata(self):
        return dumps(self.metadata())

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
