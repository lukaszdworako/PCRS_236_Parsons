from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


import json

from problems_c.c_language import *


@csrf_exempt
def visualizer_details(request):
    """
        Return json encoded dictionary ret containing trace required
        for visualizer. Contents of the ret depend on language implementation.
    """

    ret = {}
    try:
        user_script = request.POST.get("user_script")
        # add_params is always JSON encoded. 
        add_params = json.loads(request.POST.get("add_params"))
        add_params = dict(add_params)
        # Use CSRF_COOKIE as username
        add_params['user'] = request.META["CSRF_COOKIE"]

        gen = CSpecifics(add_params['user'], user_script) # create a language instance

        ret = gen.get_exec_trace(user_script, add_params)
        print(ret)

    except Exception as e:
        ret['exception'] = str(e)

    json_output = json.dumps(ret, indent=None)

    return HttpResponse(json_output)
