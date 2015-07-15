from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
from problems_c.c_language import *
from problems_c.c_utilities import *
from problems_c.models import Problem
import logging

from pprint import pprint
import pdb


def new_visualizer_details_editor(request):
    """
        Return json encoded dictionary ret containing trace required
        for the new C visualizer.
    """
    logger = logging.getLogger('activity.logging')

    ret = {}
    try:
        user_code = request.POST.get("user_code")

        # add_params is always JSON encoded.
        add_params = json.loads(request.POST.get("add_params"))
        add_params = dict(add_params)
        # Use CSRF_COOKIE as username
        add_params['user'] = request.META["CSRF_COOKIE"]
        add_params['test_case'] = ''

        # Create a language instance
        gen = CSpecifics(add_params['user'], user_code)

        hidden_lines_list = []
        ret = gen.get_exec_trace(user_code, add_params, hidden_lines_list)

    except ZeroDivisionError as e:
        ret['exception'] = str(e)


    json_output = json.dumps(ret, indent=None)
    return HttpResponse(json_output)
