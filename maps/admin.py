from django.contrib import admin
from maps.models import Task, Basemap, Heatmap

admin.site.register(Task)
admin.site.register(Basemap)
admin.site.register(Heatmap)
