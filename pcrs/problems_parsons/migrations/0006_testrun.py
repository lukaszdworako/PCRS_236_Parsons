# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-07-15 03:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('problems_parsons', '0005_remove_problem_visible_unit'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_passed', models.BooleanField()),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_parsons.Submission')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_parsons.TestCase')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]