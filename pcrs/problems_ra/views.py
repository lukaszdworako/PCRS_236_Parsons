from django.views.generic import TemplateView
from users.views_mixins import ProtectedViewMixin


class RASyntaxReferenceView(ProtectedViewMixin, TemplateView):
    """
    RA Syntax reference page.
    """
    template_name = 'problems_rdb/ra_syntax.html'