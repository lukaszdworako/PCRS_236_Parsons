from django.conf.urls import patterns, url

from problems_rdb.views import *

urlpatterns = patterns('',
    url(r'^schema/create$', SchemaCreateView.as_view(),
        name='schema_create'),
    url(r'^schema/create_and_add_dataset$',
        SchemaCreateAndAddDatasetView.as_view(),
        name='schema_create_and_add_dataset'),
    url(r'^schema/(?P<pk>[0-9]+)/delete$', SchemaDeleteView.as_view(),
        name='schema_delete'),
    url(r'^schema/(?P<pk>[0-9]+)$', SchemaDetailView.as_view(),
        name='schema_view'),
    url(r'^schema/list$', SchemaListView.as_view(),
        name='schema_list'),
    url(r'^schema/(?P<schema>[0-9]+)/dataset$', DatasetCreateView.as_view(),
        name='dataset_create'),
    url(r'^schema/(?P<schema>[0-9]+)/datasets$', DatasetsCreateView.as_view(),
        name='datasets_create'),
    url(r'^schema/(?P<schema>[0-9]+)/dataset/(?P<pk>[0-9]+)$',
        DatasetDetailView.as_view(),
        name='dataset_view'),
    url(r'^schema/(?P<schema>[0-9]+)/dataset/(?P<pk>[0-9]+)/delete$',
        DatasetDeleteView.as_view(),
        name='dataset_delete'),
    url(r'^documentation', DocumentationView.as_view(),
        name='rdb_documentation')
)