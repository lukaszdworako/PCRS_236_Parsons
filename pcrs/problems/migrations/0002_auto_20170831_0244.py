# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-31 06:44
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0001_squashed_0037_auto_20170720_1051'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2017, 9, 1, 6, 44, 23, 674027, tzinfo=utc), null=True),
        ),
    ]