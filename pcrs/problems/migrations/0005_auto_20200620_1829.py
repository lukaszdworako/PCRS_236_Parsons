# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-20 22:29
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0004_auto_20200620_1826'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 21, 22, 29, 8, 560732, tzinfo=utc), null=True),
        ),
    ]
