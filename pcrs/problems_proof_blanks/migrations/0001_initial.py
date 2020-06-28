# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-06-27 23:43
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('content', '0003_optional_description'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0001_initial'),
        ('mastery', '0002_auto_20170828_0419'),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visibility', models.CharField(choices=[('closed', 'closed'), ('open', 'open')], default='open', max_length=10)),
                ('max_score', models.SmallIntegerField(blank=True, default=0)),
                ('scaling_factor', models.FloatField(default=1)),
                ('author', models.CharField(blank=True, max_length=128)),
                ('notes', models.CharField(blank=True, max_length=256)),
                ('name', models.CharField(max_length=150)),
                ('proof_statement', models.TextField(blank=True)),
                ('incomplete_proof', models.TextField(blank=True)),
                ('no_correct_response', models.BooleanField(default=False)),
                ('answer_keys', django.contrib.postgres.fields.hstore.HStoreField(blank=True, default=None)),
                ('feedback_keys', django.contrib.postgres.fields.hstore.HStoreField(blank=True, default=None)),
                ('hint_keys', django.contrib.postgres.fields.hstore.HStoreField(blank=True, default=None)),
                ('challenge', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='problems_proof_blanks_problem_related', to='content.Challenge')),
                ('tags', models.ManyToManyField(blank=True, related_name='problems_proof_blanks_problem_related', to='content.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('submission', models.TextField(blank=True, null=True)),
                ('score', models.SmallIntegerField(default=0)),
                ('has_best_score', models.BooleanField(default=False)),
                ('mastery_quiz_session_participant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='problems_proof_blanks_submission_related', to='mastery.MasteryQuizSessionParticipant')),
                ('problem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_proof_blanks.Problem')),
                ('section', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='problems_proof_blanks_submission_related', to='users.Section')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='problems_proof_blanks_submission_related', to=settings.AUTH_USER_MODEL, to_field='username')),
            ],
        ),
    ]
