# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-07-17 01:11
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0013_auto_20200714_2310'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2020, 7, 18, 1, 11, 40, 742774, tzinfo=utc), null=True),
        ),
    ]