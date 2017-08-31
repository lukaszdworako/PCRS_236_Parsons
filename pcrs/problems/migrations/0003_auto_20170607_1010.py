# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-07 14:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0002_auto_20170606_1658'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='data',
            field=models.FileField(upload_to='languages/r/CACHE'),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2017, 6, 8, 10, 10, 39, 814820)),
        ),
    ]