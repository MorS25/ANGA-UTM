# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-06 09:07
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0013_auto_20180206_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='obstacles',
            name='geom',
            field=django.contrib.gis.db.models.fields.GeometryField(srid=4326),
        ),
    ]
