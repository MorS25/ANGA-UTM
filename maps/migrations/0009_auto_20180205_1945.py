# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-02-05 16:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0008_locationpoints_shortcode'),
    ]

    operations = [
        migrations.AlterField(
            model_name='locationpoints',
            name='shortcode',
            field=models.CharField(blank=True, max_length=3, null=True),
        ),
    ]
