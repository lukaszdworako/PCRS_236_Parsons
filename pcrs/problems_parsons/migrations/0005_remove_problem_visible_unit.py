# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-07-15 02:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('problems_parsons', '0004_auto_20200714_2216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='visible_unit',
        ),
    ]