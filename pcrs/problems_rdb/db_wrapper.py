import psycopg2
from psycopg2 import extras
from psycopg2._psycopg import DatabaseError
import re


# A pattern for finding for parsing relation and attribute names from
# the postgres pg_catalog.pg_get_constraintdef() call.
FOREIGN_KEYS_PATTERN = \
        'FOREIGN KEY ([^\\.])?\\((?P<child_cols>.+?)\\) REFERENCES ' \
        '([^\\.]*\\.)?(?P<parent>.+?)\\((?P<parent_cols>.+?)\\)'
FOREIGN_KEYS_RE = re.compile(FOREIGN_KEYS_PATTERN)


class PostgresWrapper:
    def __init__(self, database, user):
        self.database = database
        self.user = user
        self._conn = None
        self._cursor = None
        self.connect()

    def __enter__(self):
            return self

    def __exit__(self, type, value, traceback):
        self.close()

    def connect(self):
        """
        Connect to the database as the user.
        """
        self._conn = psycopg2.connect(database=self.database,
                                      user=self.user, password=self.user)
        self._cursor = self._conn.cursor(cursor_factory=extras.DictCursor)

    def close(self):
        """
        Close the database connection.
        """
        self._cursor.close()
        self._conn.close()

    def commit(self):
        """
        Commit the current transaction.
        """
        self._conn.commit()

    def rollback(self):
        """
        Rollback the current transaction.
        """
        self._conn.rollback()

    def execute(self, sql, parameters=None):
        """
        Execute the sql as parametrized query.
        """
        self._cursor.execute(sql, parameters)

    def fetchall(self):
        """
        Return the result of the last executed query.
        """
        return self._cursor.fetchall()

    def run_query(self, sql, parameters=None, schema_name=None):
        """
        Run the sql query in schema schema_name with parameters and
        return the results.
        """
        if schema_name is not None:
            self.set_schema(schema_name)
        self.execute(sql, None)
        return self.fetchall()

    def set_schema(self, schema_name):
        """
        Set the search_path to schema_name.
        """
        self.execute("SET search_path TO {name}".format(name=schema_name))

    def create_schema(self, schema_name, authorization=None, definition=None):
        """
        Create schema schema_name with authorization and definition.
        """
        sql = 'CREATE SCHEMA {name}'
        if authorization:
            sql += ' AUTHORIZATION {auth}'.format(auth=authorization)
        self.execute(sql.format(name=schema_name))
        if definition is not None:
            self.set_schema(schema_name)
            self.execute(definition)
        if authorization:
            self.grant_create_on_schema(schema_name, authorization)
            self.grant_select_on_schema(schema_name, authorization)
            self.grant_usage_on_schema(schema_name, authorization)

    def check_schema_exists(self, schema_name):
        """
        Return True if and only if schema schema_name exists in the database.
        """
        sql = ("SELECT schema_name FROM information_schema.schemata WHERE"
                     " schema_name = '{name}';".format(name=schema_name))
        self.execute(sql)
        return bool(self._cursor.rowcount)

    def drop_schema(self, schema_name):
        """
        Drop schema schema_name.
        """
        if self.check_schema_exists(schema_name):
            self.execute("DROP SCHEMA {name} CASCADE".format(name=schema_name))

    def insert_into_schema(self, schema_name, sql):
        """
        Insert the data into schema schema_name.
        """
        self.set_schema(schema_name)
        self.execute(sql)

    def grant_usage_on_schema(self, schema_name, user):
        """
        Grant usage on schema schema_name to user.
        """
        self.execute("GRANT USAGE ON SCHEMA {schema} TO {user}".format(
            schema=schema_name, user=user))

    def grant_select_on_schema(self, schema_name, user):
        """
        Grant usage on schema schema_name to user.
        """
        self.execute(
            "GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {user}".format(
                schema=schema_name, user=user))

    def grant_create_on_schema(self, schema, user):
        """
        Grant create on schema schema_name to user.
        """
        self.execute(
            "GRANT CREATE ON SCHEMA {schema} TO {user}".format(
                schema=schema, user=user))

    def validate(self, definition, data=None, query=None):
        """
        Validate the schema by attempting to create a schema with the
        provided definition.
        Validate the data by attempting to insert it into the tables.
        Validate the query by attempting to run it.
        """
        try:
            test_schema = 'test_'
            self.create_schema(test_schema, None, definition)
            if data:
                self.insert_into_schema(test_schema, data)
            if query:
                self.execute(query)
        finally:
            self.rollback()

    def get_information(self, definition):
        """
        Return a dictionary representing the schema definition.

        The dictionary has three keys: tables, pkeys, and fkeys representing
        the list of tables and their attributes, the mapping of table names
        to the lists of their primary keys, and the list of tuples
        representing the foreign key pairs.
        """
        try:
            test_schema = 'test_'
            self.create_schema(test_schema, None, definition)
            tables = self.get_tables_to_columns(test_schema)
            pkeys = self.get_primary_keys(test_schema)
            fkeys = self.get_foreign_keys(test_schema)
            return {'tables': tables, 'pkeys': pkeys, 'fkeys': fkeys}
        finally:
            self.rollback()

    def get_tables_to_columns(self, schema_name):
        sql = "SELECT table_name, column_name FROM " \
              "information_schema.tables" \
              " NATURAL JOIN information_schema.columns " \
              "WHERE table_schema='{name}';".format(name=schema_name)
        return self._get_table_to_attrs(sql)

    def get_primary_keys(self, schema_name):
        sql = "select table_name, column_name from " \
              "information_schema.constraint_column_usage where " \
              "constraint_name like '%_pkey' and table_schema='{name}';"\
            .format(name=schema_name)
        return self._get_table_to_attrs(sql)

    def get_foreign_keys(self, schema_name):
        # Postgres specific query that gets information about foreign keys in the
        # namespace.
        sql = "SELECT r.conrelid::regclass AS child_name, " \
              "pg_catalog.pg_get_constraintdef(r.oid, TRUE) AS constraint_def " \
              "FROM pg_catalog.pg_constraint r " \
              "WHERE r.contype = 'f' AND " \
              "connamespace = (SELECT oid FROM pg_namespace " \
              "WHERE nspname = '{name}');".format(name=schema_name)

        foreign_keys = []
        for dictionary in self.run_query(sql):
            child = dictionary['child_name'].split('.')[-1]
            constraint_def = dictionary['constraint_def']
            matcher = FOREIGN_KEYS_RE.match(constraint_def)
            child_cols, parent, parent_cols = matcher.group(
                'child_cols', 'parent', 'parent_cols')
            foreign_keys.append(((child, child_cols), (parent, parent_cols)))
        return foreign_keys

    def _get_table_to_attrs(self, sql):
        table_to_attrs = {}
        for dictionary in self.run_query(sql):
            table = dictionary['table_name']
            attribute = dictionary['column_name']
            table_to_attrs[table] = table_to_attrs.get(table, []) + [attribute]
        return table_to_attrs

    @staticmethod
    def html_representation(info):
        """
        Construct an html-formatted schema representation.

        A schema representation includes a list of table names followed by
        a parenthesized comma-separated list of its attributes, with primary
        keys underlined, as well as the list of foreign keys in the format
        table[attribute] < table[attribute].
        """
        repr, constraints = [], []
        primary_keys = info.get('pkeys', {})
        for table, attrs in info['tables'].items():
            keys = primary_keys.get(table, [])
            attributes = ['<u>{0}</u>'.format(attr) if attr in keys else attr
                          for attr in attrs]
            repr.append('<b>{table}</b>({attributes})'.format(
                table=table, attributes=', '.join(attributes)))

        for (table, attrs), (ref_table, ref_attrs) in info.get('fkeys', {}):
            fkey_str = '{table1}[{attr1}] &sube; {table2}[{attr2}]'.format(
                table1=table, attr1=attrs,
                table2=ref_table, attr2=ref_attrs)
            constraints.append(fkey_str)
            print(table, attrs, ' '.join(attrs), ref_table, ref_attrs)
        return '<br><br>'.join(['<br>'.join(repr), '<br>'.join(constraints)])


class StudentWrapper(PostgresWrapper):
    @staticmethod
    def process(expected, actual, order_matters):
        """
        Returns True iff expected and actual are the same,
        or contain the same items in a different order, and order_matters is
        False; otherwise returns False.

        Processes the result sets and marks results in actual as extra if they
        do not appear in the expected, marks results in expected as
        missing if they do not appear in actual.
        Marks result as out of order, if it is not extra, and the number of
        results in actual is the same as in the expected.

        ALTERS OBJECTS IN expected AND actual.
        """
        def _to_tuple(d):
            return tuple(sorted(d.items()))

        # construct the dictionaries storing how many times we've seen each
        # record, and how many times we expected to see it
        actual_to_count = {}
        expected_to_count = {}
        for row in actual:
            key = _to_tuple(row)  # dicts are not hashable, so make a tuple
            actual_to_count[key] = actual_to_count.get(key, 0) + 1

        for row in expected:
            key = _to_tuple(row)
            expected_to_count[key] = expected_to_count.get(key, 0) + 1

        same = expected == actual if order_matters else \
               expected_to_count == actual_to_count

        # for every record, check if we see it more times than we should,
        # and mark extra records with 'extra' = True
        seen = {}
        for i in range(len(actual)):
            row = actual[i]
            key = _to_tuple(row)
            seen[key] = seen.get(key, 0) + 1
            should_see = expected_to_count.get(key, 0)
            extra = seen[key] > should_see
            # ordering is only meaningful if the number of results is the same
            if not extra and order_matters and len(expected) == len(actual):
                row['out_of_order'] = actual[i] != expected[i]
            row['extra'] = extra

        # for every record that we should have seen, but didn't,
        # mark the records with 'missing' = True
        seen = {}
        for row in expected:
            key = _to_tuple(row)
            seen[key] = seen.get(key, 0) + 1
            actually_see = actual_to_count.get(key, 0)
            row['missing'] = seen[key] > actually_see

        return same

    def run_testcase(self, solution, submission, namespace,
                     order_matters=False):
        """
        Run a single testcase:
        run the solution and the submission within the namespace, and
        compare the results.

        Return a dictionary representing this test run.

        """
        result = {'expected_attrs': None,
                  'actual_attrs': None,
                  'passed': False, 'error': None,
                  'expected': None,
                  'actual': None}
        try:
            result['expected'] = self.run_query(solution, schema_name=namespace)
            result['expected_attrs'] = [d[0] for d in self._cursor.description]

            L = result['expected_attrs']
            for index in range(len(L)):
                count = L[: index].count(L[index])
                if count > 0:
                    L[index] = L[index] + " (" + str(count + 1) + ")"

            cursor = result['expected']
            for cursor_index in range(len(cursor)):
                d = {}
                item = cursor[cursor_index]
                for index in range(len(L)):
                    d[L[index]] = item[index]
                cursor[cursor_index] = d
            
            self.rollback()

            result['actual'] = self.run_query(submission, schema_name=namespace)
            result['actual_attrs'] = [d[0] for d in self._cursor.description]

            L = result['actual_attrs']
            for index in range(len(L)):
                count = L[: index].count(L[index])
                if count > 0:
                    L[index] = L[index] + " (" + str(count + 1) + ")"  
                    
            cursor = result['actual']
            for cursor_index in range(len(cursor)):
                d = {}
                item = cursor[cursor_index]
                for index in range(len(L)):
                    d[L[index]] = item[index]
                cursor[cursor_index] = d          
            
            result['passed'] = self.process(result['expected'],
                                            result['actual'],
                                            order_matters)
        except DatabaseError as e:
            result['error'] = '{code}: {message}'.format(code=e.pgcode,
                                                         message=e.pgerror)

        finally:
            self.rollback()
            return result


class InstructorWrapper(StudentWrapper):
    def create_dataset(self, schema_name, schema_definition, data,
                       usergroup='students'):
        self.create_schema(schema_name, authorization='instructors',
                           definition=schema_definition)

        self.insert_into_schema(schema_name, data)
        self.grant_usage_on_schema(schema_name, usergroup)
        self.grant_select_on_schema(schema_name, usergroup)
        self.grant_create_on_schema(schema_name, usergroup)

    def create_datasets(self, name_prefix, definition, datasets):
        datasets = [dataset for dataset in datasets if dataset]
        try:
            for dataset in datasets:
                schema_name = name_prefix + '_' + dataset['name']
                self.create_dataset(schema_name=schema_name,
                                    schema_definition=definition,
                                    data=dataset['definition'],
                                    usergroup='students')
        except DatabaseError as e:
            self.rollback()
            raise e
