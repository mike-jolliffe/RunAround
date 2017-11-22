from django.contrib.gis.db import models


class Segment(models.Model):
    seg_id = models.IntegerField(null=True)
    attempts = models.IntegerField('Total Attempts at Segment', null=True)
    distance = models.FloatField('Total Distance of Segment', null=True)
    geom = models.MultiPointField()

    def __str__(self):
        return str(self.seg_id)
