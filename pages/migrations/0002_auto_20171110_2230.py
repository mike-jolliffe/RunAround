# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-10 22:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='distance',
            field=models.FloatField(null=True, verbose_name='Total Distance of Segment'),
        ),
        migrations.AlterField(
            model_name='segment',
            name='attempts',
            field=models.IntegerField(null=True, verbose_name='Total Attempts at Segment'),
        ),
    ]
