# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2020-07-16 02:00
from __future__ import unicode_literals

import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('problems_proof_blanks', '0002_auto_20200713_2039'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_keys', django.contrib.postgres.fields.hstore.HStoreField(blank=True, default=None, null=True)),
                ('hint_keys', django.contrib.postgres.fields.hstore.HStoreField(blank=True, default=None, null=True)),
            ],
            options={
                'ordering': ['pk'],
            },
        ),
        migrations.RemoveField(
            model_name='problem',
            name='feedback_keys',
        ),
        migrations.RemoveField(
            model_name='problem',
            name='hint_keys',
        ),
        migrations.AddField(
            model_name='feedback',
            name='problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='problems_proof_blanks.Problem'),
        ),
    ]