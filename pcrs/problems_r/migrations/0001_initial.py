# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-06-06 18:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import problems.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('visibility', models.CharField(choices=[('closed', 'closed'), ('open', 'open')], default='open', max_length=10)),
                ('max_score', models.SmallIntegerField(blank=True, default=0)),
                ('starter_code', models.TextField(blank=True)),
                ('solution', models.TextField(blank=True)),
                ('language', models.CharField(choices=[('r', 'R 3.3.2')], default='r', max_length=50)),
                ('sol_graphics', models.TextField(blank=True, null=True)),
                ('output_visibility', models.BooleanField(default=True)),
                ('challenge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='problems_r_problem_related', to='content.Challenge')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Script',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(max_length=30, unique=True)),
                ('code', models.TextField()),
                ('expected_output', models.TextField(blank=True, null=True)),
                ('graphics', models.TextField(blank=True, null=True)),
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
                ('score', models.SmallIntegerField(default=0)),
                ('has_best_score', models.BooleanField(default=False)),
                ('passed', models.BooleanField()),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_r.Problem')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='problems_r_submission_related', to='users.Section')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='problems_r_submission_related', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
            bases=(problems.models.SubmissionPreprocessorMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TestCase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_visible', models.BooleanField(default=False, verbose_name='Testcase visible to students')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_r.Problem')),
            ],
            options={
                'ordering': ['pk'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TestRun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('test_passed', models.BooleanField()),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_r.Submission')),
                ('testcase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_r.TestCase')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='problem',
            name='script',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='problems_r.Script'),
        ),
        migrations.AddField(
            model_name='problem',
            name='tags',
            field=models.ManyToManyField(blank=True, null=True, related_name='problems_r_problem_related', to='content.Tag'),
        ),
    ]