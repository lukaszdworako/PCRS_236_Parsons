# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-06-20 22:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0003_auto_20171027_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fileupload',
            name='lifespan',
            field=models.DateTimeField(default=datetime.datetime(2020, 6, 21, 22, 25, 50, 155340, tzinfo=utc), null=True),
        ),
    ]
