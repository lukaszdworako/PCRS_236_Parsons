# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-08-08 03:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_pcrsuser_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pcrsuser',
            name='password',
        ),
    ]
