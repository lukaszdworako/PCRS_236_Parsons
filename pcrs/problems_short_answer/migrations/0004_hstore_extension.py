from django.contrib.postgres.operations import HStoreExtension
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('problems_short_answer', '0003_problem_author'),
    ]

    operations = [
        HStoreExtension()
    ]
