# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-06-30 03:35
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0006_auto_20200629_1716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 1, 3, 34, 56, 706394, tzinfo=utc), null=True),
        ),
    ]