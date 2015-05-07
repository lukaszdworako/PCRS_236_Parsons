import json
import datetime
import logging

from django.http import HttpResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.views.generic import (DetailView, UpdateView, DeleteView, FormView,
                                  View)
from django.views.generic.detail import SingleObjectMixin
from django.utils.timezone import localtime

from pcrs.generic_views import (GenericItemCreateView, GenericItemListView,
                                GenericItemUpdateView)

class EditorView():
