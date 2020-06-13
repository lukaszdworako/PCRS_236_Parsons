# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 14:52
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('src', models.TextField(blank=False, null=False)),
                ('invariant', models.TextField(blank=False, null=False)),
                ('unit_tests', models.TextField(blank=True, null=True)),
                ('run_unit', models.BooleanField(default=False)),
                ('visible_unit', models.BooleanField(default=False)),
                ('static', models.TextField(blank=True, null=True)),
                ('groups', models.TextField(blank=True, null=True)),
                ('inter', models.TextField(blank=True, null=True)),
                ('solution', models.TextField(blank=False, null=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('submission', models.TextField(blank=True, null=True)),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_short_answer.Problem')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='problems_short_answer_submission_related', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
    ]
