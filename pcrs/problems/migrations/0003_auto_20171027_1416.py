# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-27 18:16
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0002_auto_20170831_0244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2017, 10, 28, 18, 16, 45, 63635, tzinfo=utc), null=True),
        ),
    ]