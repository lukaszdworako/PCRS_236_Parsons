from json import dumps
from psycopg2._psycopg import Error as psycopgError

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete

from pcrs.model_helpers import has_changed, get_stored_value
from problems.models import (AbstractSelfAwareModel, AbstractProgrammingProblem,
                             AbstractTestCase)
from problems_rdb.db_wrapper import InstructorWrapper


class Schema(AbstractSelfAwareModel):
    """
    A database schema. A Schema consists of a name and a definition.

    The definition is expected to be valid SQL DDL.

    The name (limited to 30 characters) will be prefixed to a Dataset name to
    create a unique name for a namespace. As common SQL implementations limit
    names to 64 characters, the name is limited to 30.

    When a Schema is deleted, any associated Datasets are also deleted.
    """
    name = models.SlugField(max_length=30, unique=True)
    definition = models.TextField(blank=False, null=False)
    representation = models.TextField(blank=False, null=False)
    tables = models.TextField(null=False)

    @classmethod
    def get_db(cls):
        """
        Return a connection to the database where the namespaces for
        this schema would be created.
        """
        return _get_db()

    @classmethod
    def get_base_url(cls):
        """
        Return the url for a schema.
        """
        return '{prefix}/problems/rdb/schema'.format(prefix=settings.SITE_PREFIX)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '{base}/{pk}'.format(base=self.get_base_url(), pk=self.pk)

    def clean_fields(self, exclude=None):
        """
        Clean the fields before creating a Schema instance.

        Populate the tables and representation fields.
        Raise ValidationError if schema definition is invalid.
        """
        self.name = self.name.replace('-', '_')
        if not self.name:
            raise ValidationError({'name': ['This field is required.']})

        if self.name and self.name[0].isnumeric():
            raise ValidationError({'name': ['Cannot begin with a number.']})

        if self.definition and not self.representation:
            with self.get_db() as db:
                try:
                    info = db.get_information(self.definition)
                    if not info['tables']:
                        raise ValidationError({'definition': [
                            'Could not construct schema representation.'
                        ]})
                    self.tables = dumps(info['tables'])
                    repr = db.html_representation(info)
                    self.representation = repr
                    super().clean_fields(exclude)
                except psycopgError as pgerror:
                    error = 'Schema definition is invalid.'
                    error_message = pgerror.pgerror
                    raise ValidationError({'definition': [error, error_message]})


class Dataset(AbstractSelfAwareModel):
    """
    A collection of data. A Dataset consists of a name, a definition for
    the data and an associated Schema.

    The definition for the data is expected to be valid SQL DML.

    A Dataset along with its associated Schema is used to create a namespace
    within the database.

    The name (limited to 30 characters) will be appended to a Schema name to
    create a unique name for a namespace. As common SQL implementations limit
    names to 64 characters, the name is limited to 30.

    When a Dataset or a Schema is deleted, any associated SQLTestCases are
    also deleted.
    """
    name = models.SlugField(max_length=30, blank=False, null=False)
    schema = models.ForeignKey(Schema, on_delete=models.CASCADE, blank=False,
                               null=False)
    definition = models.TextField(blank=False, null=False)

    class Meta:
        unique_together = ('name', 'schema')

    @classmethod
    def get_db(cls):
        """
        Return a connection to the database where the namespace for
        this dataset is created.
        """
        return _get_db()

    @property
    def namespace(self):
        return '{0}_{1}'.format(self.schema.name, self.name)

    def __str__(self):
        return '{0}_{1}'.format(self.schema, self.name)

    def get_absolute_url(self):
        return '{schema}/dataset/{pk}'\
            .format(schema=self.schema.get_absolute_url(), pk=self.pk)

    def clean_fields(self, exclude=None):
        """
        Clean the fields before creating a Dataset instance.

        Validate the dataset definition against its schema definition.
        Raise an error if schema definition does not exist, or if the dataset
        definition is invalid within the schema.
        """
        self.name = self.name.replace('-', '_')
        super().clean_fields(exclude)

        with self.get_db() as db:
            try:
                db.validate(definition=self.schema.definition,
                            data=self.definition)
            except psycopgError as pgerror:
                error = 'Dataset definition is invalid.'
                error_message = pgerror.pgerror
                raise ValidationError({'definition': [error, error_message]})
            except Schema.DoesNotExist:
                # There is already an error generated for this, so we do not
                # need to add an extra one.
                pass

    def save(self, *args, **kwargs):
        """
        Save the dataset instance to the Django database.

        Crete the namespace with the dataset data definition.
        """
        with self.get_db() as db:
            try:
                # Drop the current namespace in the data database if one exists,
                # and create the new one
                db.drop_schema(self.namespace)
                db.create_dataset(self.namespace, self.schema.definition,
                                  self.definition)
                super().save(*args, **kwargs)
                db.commit()
            except psycopgError as e:
                db.rollback()
                raise ValueError('Dataset definition is invalid: {db_error}'
                                 .format(db_error=e.pgerror))


class RDBProblem(AbstractProgrammingProblem):
    """
    A Relational DataBase problem.

    Extends problem, and has an additional attributes that is the Schema
    to be used for the problem.
    """

    schema = models.ForeignKey(Schema, on_delete=models.CASCADE,
                               blank=False, null=False,
                               related_name='%(app_label)s_%(class)s_related')

    class Meta:
        abstract = True

    @classmethod
    def get_db(cls):
        return _get_db()

    def clean_fields(self, exclude=None):
        """
        Clean the fields before creating a problem instance.

        Changing some fields affects the correctness of submissions, and
        requires submissions to be cleared.
        The fields are defined in affect_submissions property.
        Schema change always requires clearing submissions.
        """
        super().clean_fields(exclude)

        # validate the solution
        if has_changed(self, 'solution') and not 'schema' in exclude:
            self.validate_solution()

        if self.submission_set.exists():
            error = 'Submissions must be cleared.'
            # Note that self.schema in the current context is an object, but
            # the value currently in the db is an int that is the schema's pk.
            current_schema_pk = get_stored_value(self, 'schema')
            if current_schema_pk != self.schema.pk:
                raise ValidationError({'schema': [error]})
            for field in self.affect_submissions:
                if has_changed(self, field):
                    raise ValidationError({field: [error]})

    def _run_solution(self, solution):
        """
        Run the problem solution to validate it against the schema.
        """
        with self.get_db() as db:
            try:
                db.validate(definition=self.schema.definition,
                            query=solution)
            except psycopgError as e:
                raise ValidationError({'solution': [e.pgerror]})
            except Schema.DoesNotExist:
            # There is already an error generated for this, so we do not
            # need to add an extra one.
                pass


class RDBTestCase(AbstractTestCase):
    """
    A test case for an RDB problem. An RDBTestCase is associated with a
    single Dataset.

    When a Dataset or a RDBProblem is deleted, any associated RDBTestCases
    are also deleted.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=False,
                                related_name='%(app_label)s_%(class)s_related')

    class Meta:
        abstract = True

    def __str__(self):
        return self.dataset.name


def _get_db():
    """
    Return a connection to the database where the namespace for
    the RDB problems will be created.
    """
    return InstructorWrapper(database=settings.RDB_DATABASE, user='instructor')


def delete_namespace(sender, instance, **kwargs):
    """
    Delete the namespace associated with the deleted dataset instance.
    """
    with instance.get_db() as db:
        try:
            db.drop_schema(str(instance))
            db.commit()
        except psycopgError as e:
            db.rollback()
            raise Exception(e.pgerror)

# delete the namespace for the dataset to be deleted
pre_delete.connect(delete_namespace, sender=Dataset)
