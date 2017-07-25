# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-09 01:45
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0009_auto_20170608_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='data',
            field=models.BinaryField(),
        ),
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2017, 6, 10, 1, 45, 59, 71403, tzinfo=utc), null=True),
        ),
    ]
