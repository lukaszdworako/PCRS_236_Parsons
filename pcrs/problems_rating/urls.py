from django.conf.urls import url

from problems.views import (ProblemCreateView, ProblemListView,
                            ProblemUpdateView, ProblemClearView,
                            ProblemDeleteView)
from problems_rating.models import (Problem, Submission)
from problems_rating.forms import (ProblemForm, ProblemUpdateForm)
from problems_rating.views import (SubmissionView, SubmissionAsyncView)

urlpatterns = [

    url(r'^list$',
        ProblemListView.as_view(model=Problem),
        name='rating_list'),

    url(r'^create$',
        ProblemCreateView.as_view(model=Problem, form_class=ProblemForm),
        name='rating_create'),

    url(r'^(?P<pk>[0-9]+)/?$',
        ProblemUpdateView.as_view(model=Problem, form_class=ProblemUpdateForm,
        template_name='pcrs/item_form.html'),
        name='rating_update'),

    url(r'^(?P<pk>[0-9]+)/clear$',
        ProblemClearView.as_view(model=Problem),
        name='rating_clear'),

    url(r'^(?P<pk>[0-9]+)/delete$',
        ProblemDeleteView.as_view(model=Problem),
        name='rating_delete'),

    url(r'^(?P<problem>[0-9]+)/submit$',
        SubmissionView.as_view(),
        name='rating_submit'),

    url(r'^(?P<problem>[0-9]+)/run$',
        SubmissionAsyncView.as_view(model=Submission),
        name='rating_async_submit'),

]
