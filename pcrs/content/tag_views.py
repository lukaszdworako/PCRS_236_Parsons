import json

from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.generic import ListView

from content.forms import TagForm
from content.tags import Tag

from pcrs.generic_views import (GenericItemListView, GenericItemCreateView,
                                GenericItemUpdateView)
from users.views_mixins import CourseStaffViewMixin


class TagListView(CourseStaffViewMixin, GenericItemListView):
    """
    List all Tags.
    """
    model = Tag
    template_name = 'pcrs/item_list.html'


class TagDetailEntry(CourseStaffViewMixin):
    model = Tag
    template_name = 'pcrs/crispy_form.html'
    form_class = TagForm


class TagCreateView(TagDetailEntry, GenericItemCreateView):
    """
    Create a new Tag.
    """
    def post(self, request, *args, **kwargs):
        # We want a JSON response for AJAX calls
        if request.is_ajax():
            result = self.ajaxPost(request)
            return HttpResponse(json.dumps(result), mimetype='application/json')
        else:
            return super().post(request, *args, **kwargs)

    def ajaxPost(self, request):
        try:
            self.object = Tag(name=request.POST.get('name'))
            self.object.full_clean() # Required for validation
            self.object.save()
            return {
                'pk': self.object.pk,
                'name': self.object.name,
            }
        except ValidationError as e:
            return {
                # Probably an error with 'name'
                'validation_error': e.message_dict,
            }


class TagUpdateView(TagDetailEntry, GenericItemUpdateView):
    """
    Update a Tag.
    """
