import json
from django.http import HttpResponseRedirect
from django.views.generic import FormView
from content.forms import ContentImportForm
from io import TextIOWrapper
from django.contrib.contenttypes.models import ContentType

class ImportView(FormView):
    form_class = ContentImportForm
    template_name = "content/import.html"

    def post(self, request):
        json_file = TextIOWrapper(request.FILES['json_file'].file, encoding='utf-8')
        with json_file as jf:
            json_data = json.loads(r'{}'.format(jf.read()))

        pk_to_problems = {}
        
        for pcrs_obj in json_data:
            model_field = pcrs_obj['model'].split('.')
            model = ContentType.objects.get(app_label=model_field[0], model=model_field[1]).model_class()
            for field in list(pcrs_obj['fields'].keys()):
                    if field not in [f.name for f in model._meta.fields]:
                        pcrs_obj['fields'].pop(field)
            if model_field[1] == "problem" and 'max_score' in pcrs_obj['fields']:
                pcrs_obj['fields']['max_score'] = 0
                        
            if model_field[1] in ("testcase", "option"):
                pcrs_obj['fields']['problem'] = pk_to_problems[pcrs_obj['fields']['problem']]
            obj = model.objects.create(**pcrs_obj['fields'])
            if model_field[1] == "problem":
                pk_to_problems[pcrs_obj['pk']] = obj
                
        return HttpResponseRedirect('/')
