# -*- coding: utf-8 -*-
"""
This migration is for adding the HStore Extension to the db. If the configured
database user doesn't have super user privileges then this migration will fail.
If that is the case, the user must directly add the HStore Extension in Postgres
with a user that has the appropriate privileges. Run this query:
    CREATE EXTENSION IF NOT EXISTS hstore;
"""
from __future__ import unicode_literals
from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems_short_answer', '0006_problem_min_chars'),
    ]

    operations = [
        HStoreExtension(),
    ]
