# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-06 20:58
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2017, 6, 7, 16, 58, 34, 212596)),
        ),
    ]