# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-16 07:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utm_messages', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usertousermessages',
            name='date_modified',
        ),
    ]
