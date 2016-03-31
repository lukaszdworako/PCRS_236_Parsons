import json

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from problems_python.pcrs_languages import *


@csrf_exempt
def visualizer_details(request):
    """
        Return json encoded dictionary ret containing trace required
        for visualizer. Contents of the ret depend on language implementation.
    """

    ret = {}
    try:
        language = request.POST.get("language")
        user_script = request.POST.get("user_script")
        # add_params is always JSON encoded.
        add_params = json.loads(request.POST.get("add_params"))
        add_params = dict(add_params)

        gen = GenericLanguage(language) # create a language instance

        ret = gen.get_exec_trace(user_script, add_params)

    except Exception as e:
        ret['exception'] = str(e)

    json_output = json.dumps(ret, indent=None)

    return HttpResponse(json_output)
