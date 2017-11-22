from django.contrib.gis import admin
from pages.models import Segment

admin.site.register(Segment, admin.GeoModelAdmin)