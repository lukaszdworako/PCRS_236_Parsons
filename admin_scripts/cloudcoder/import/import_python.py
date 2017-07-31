"""
Usage:
  import_python.py <importfile.json>
"""

######################################################################
# Setting up PCRS on Andrew's local machine. Follow your own path.

import sys
sys.path.append("/Users/peters43/projects/pcrs/utmandrew/pcrs")
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pcrs.settings")
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

import json

from pcrs import settings
from problems_python.models import Problem, TestCase


######################################################################
# Extracting data from the file and loading each problem

if __name__ == '__main__':
    from docopt import docopt
    args = docopt(__doc__)
    fname = args.get('<importfile.json>')
    with open(fname) as f:
        data = json.loads(f.read())


    # Assuming a CloudCoder data format:
    # [ "problemset_name",
    #    {problem1 ...},
    #    {problem2 ...},
    #    {problemN ...}
    # ]
    print("Importing from", data[0])
    for problem in data[1:]:
        problem_data = problem['problem_data']
        testcases = problem['test_case_data_list']

        if problem_data['problem_type'] != 1 or \
           problem_data['schema_version'] not in [1, 4, 7] or \
           problem_data['license'] != 1:
            print("Issue encountered in problem import: {0}".format(problem_data['brief_description']), file=sys.stderr)
            if problem_data['problem_type'] == 4:
                print("\tProblem requires STDIN")
            else:
                print("\t", problem_data['problem_type'], problem_data['schema_version'], problem_data['license'], file=sys.stderr)
            continue

        pd = {}
        pd['name'] = '{} (CC)'.format(problem_data['brief_description'])
        pd['description'] = problem_data['description']
        if problem_data['author_name']:
            pd['author'] = '{} ({})'.format(problem_data['author_name'], problem_data['author_email'])
        else:
            pd['author'] = 'Source: CloudCoder'
        pd['visibility'] = 'open'
        pd['language'] = 'python'

        # All CC code is a fragment to be filled in by the student
        pd['starter_code'] = '''[student_code]
{}
[/student_code]'''.format(problem_data['skeleton'])

        p = Problem(**pd)
        p.save()

        # TODO: tests broken ... build TestCase instances
        # Tests are defined as test inputs to a specific function name
        testname = problem_data['testname']
        for t in testcases:
            tc = {'problem': p, 'is_visible': False}
            tc['description'] = t['test_case_name']
            tc['test_input'] = '{}({})'.format(testname, t['input'])
            tc['expected_output'] = t['output']
            test = TestCase(**tc)
            test.save()

