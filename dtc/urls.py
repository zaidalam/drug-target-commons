"""dtc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from tastypie.api import Api
from dtc.api.resources import ActivityResource
from . import views
# from dtc.admin import admin_site

v1_api = Api(api_name='data')
v1_api.register(ActivityResource())

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.home, name='home'),
    url(r'^bulk_import/$', views.bulk_import, name='bulk_import'),
    url(r'^submissions/$', views.submissions, name='submissions'),
    url(r'^getsubmissions/$', views.getsubmissions, name='getsubmissions'),
    url(r'^getallsubmissions/$', views.getallsubmissions, name='getallsubmissions'),
    url(r'^get_annotations$', views.get_annotations, name='get_annotations'),
    url(r'^search$', views.search,name='search'),
    url(r'^userguide/$', views.userguide, name='userguide'),
    url(r'^reference/$', views.reference, name='reference'),
    url(r'^glossary/$', views.glossary, name='glossary'),
    url(r'^annotation_guidlines/$', views.annotation_guidlines, name='annotation_guidlines'),
    url(r'^autosuggest/$', views.autosuggest,name='autosuggest'),
    url(r'^initial_search/$', views.initial_search,name='initial_search'),
    url(r'^bioactivities$', views.bioactivities,name='bioactivities'),
    url(r'^getbioactivities/$', views.getbioactivities,name='getbioactivities'),
    url(r'^upload_annotations/$', views.upload_annotations,name='upload_annotations'),
    url(r'^send_review/$', views.send_review,name='send_review'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^annotations$', views.annotations,name='annotations'),
    url(r'^export_to_excell/$', views.export_to_excell,name='export_to_excell'),
    url(r'^api/', include(v1_api.urls)),
    # url(r'^api/bioactivity/', include("dtc.api.urls",namespace='bioactivity-api')),
    url(r'^process_submissions/$', views.process_submissions,name='process_submissions'),
    url(r'^getcrfinfo$', views.getcrfinfo, name='getcrfinfo'),
    url(r'^gettargetcrfinfo$', views.gettargetcrfinfo, name='gettargetcrfinfo'),
    url(r'^getmutantinfo$', views.getmutantinfo, name='getmutantinfo'),
    url(r'^targetdiseaseinfo$', views.targetdiseaseinfo, name='targetdiseaseinfo'),
    url(r'^diseaseinfo$', views.diseaseinfo, name='diseaseinfo'),
    url(r'^edit_submissions/$', views.edit_submissions,name='edit_submissions'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
