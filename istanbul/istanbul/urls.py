"""istanbul URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import settings
from . import views
from installations.views import nlogin, login_as_user, npermission  #, \
#    SystemDetails, SystemEdit, InstallationDetails, InstallationEdit
from installations.viewsbasic import SystemDetails, SystemEdit, SystemList, \
    InstallationDetails, InstallationEdit, InstallationList, InstallationMap, InstallationListMap, InstallationFocusMap, \
    InstallationTypeDetails, InstallationTypeEdit, InstallationTypeList, \
    PersonEdit, PersonDetails, PersonList, \
    PurposeEdit, PurposeDetails, PurposeList, \
    LocationEdit, LocationDetails, LocationList, \
    LiteratureEdit, LiteratureDetails, LiteratureList, \
    EventEdit, EventDetails, EventList, \
    InstitutionEdit, InstitutionDetails, InstitutionList, \
    ImageEdit, ImageDetails, ImageList, \
    PersonSymbolEdit, PersonSymbolDetails, PersonSymbolList, \
    PersonTypeEdit, PersonTypeDetails, PersonTypeList, \
    ReligionEdit, ReligionDetails, ReligionList
# These are NOT needed (see issue #65)
    # EventLiteratureRelationEdit, EventLiteratureRelationDetails, \
    #SystemLiteratureRelationEdit, SystemLiteratureRelationDetails, SystemLiteratureRelationList
# Based on BasicEdit, BasicList
from installations.viewsbasic import \
    EventTypeEdit, EventTypeDetails, EventTypeList, \
    TextTypeEdit, TextTypeDetails, TextTypeList, \
    InstitutionTypeEdit, InstitutionTypeDetails, InstitutionTypeList, \
    EventRoleEdit, EventRoleDetails, EventRoleList, \
    PersonTypeEdit, PersonTypeDetails, PersonTypeList, \
    PersonSymbolEdit, PersonSymbolDetails, PersonSymbolList
from accounts.views import RegisterView
from cms.views import CitemDetails, CitemEdit,CitemListView, CitemSafe, \
    CpageDetails, CpageEdit, CpageListView, CpageAdd, \
    ClocationAdd, ClocationDetails, ClocationEdit, ClocationListView, \
    ChelpDetails, ChelpEdit, ChelpListView, \
    csettings

urlpatterns = [
    path('admin/', admin.site.urls),
	path('accounts/',include('accounts.urls')),
	path('accounts/',include('django.contrib.auth.urls')),
	path('utilities/',include('utilities.urls')),
	path('installations/',include('installations.urls', namespace='inst_main')),
	path('',include('installations.urls', namespace='inst_zero')),
	path('npermission/', npermission, name='npermission'),

    # ================== Select 2 ================================
	re_path(r'^select2/', include('django_select2.urls')),

	# ================== Removed and unnecessary Views ===================================
	# re_path('eventliterature/edit(?:/(?P<pk>\d+))?/$', EventLiteratureRelationEdit.as_view(), name='eventliteraturerelation_edit'),
	# re_path('eventliterature/details(?:/(?P<pk>\d+))?/$', EventLiteratureRelationDetails.as_view(), name='eventliteraturerelation_details'),

	# re_path('systemliterature/edit(?:/(?P<pk>\d+))?/$', SystemLiteratureRelationEdit.as_view(), name='systemliteraturerelation_edit'),
	# re_path('systemliterature/details(?:/(?P<pk>\d+))?/$', SystemLiteratureRelationDetails.as_view(), name='systemliteraturerelation_details'),

	# ================== Views ===================================
	re_path('event/edit(?:/(?P<pk>\d+))?/$', EventEdit.as_view(), name='event_edit'),
	re_path('event/details(?:/(?P<pk>\d+))?/$', EventDetails.as_view(), name='event_details'),
	re_path('event/list/$', EventList.as_view(), name='event_list'),

	re_path('image/edit(?:/(?P<pk>\d+))?/$', ImageEdit.as_view(), name='image_edit'),
	re_path('image/details(?:/(?P<pk>\d+))?/$', ImageDetails.as_view(), name='image_details'),
	re_path('image/list/$', ImageList.as_view(), name='image_list'),

	re_path('installation/edit(?:/(?P<pk>\d+))?/$', InstallationEdit.as_view(), name='installation_edit'),
	re_path('installation/details(?:/(?P<pk>\d+))?/$', InstallationDetails.as_view(), name='installation_details'),
	re_path('installation/focus(?:/(?P<pk>\d+))?/$', InstallationFocusMap.as_view(), name='installation_focus_map'),
	re_path('installation/list/$', InstallationList.as_view(), name='installation_list'),
	# re_path('installation/list/map(?:/(?P<pk>\d+))?/$', InstallationListMap.as_view(), name='installation_listmap'),
	re_path('installation/map/$', InstallationMap.as_view(), name='installation_map'),

	re_path('instaltype/edit(?:/(?P<pk>\d+))?/$', InstallationTypeEdit.as_view(), name='installationtype_edit'),
	re_path('instaltype/details(?:/(?P<pk>\d+))?/$', InstallationTypeDetails.as_view(), name='installationtype_details'),
	re_path('instaltype/list/$', InstallationTypeList.as_view(), name='installationtype_list'),

	re_path('institution/edit(?:/(?P<pk>\d+))?/$', InstitutionEdit.as_view(), name='institution_edit'),
	re_path('institution/details(?:/(?P<pk>\d+))?/$', InstitutionDetails.as_view(), name='institution_details'),
	re_path('institution/list/$', InstitutionList.as_view(), name='institution_list'),

	re_path('literature/edit(?:/(?P<pk>\d+))?/$', LiteratureEdit.as_view(), name='literature_edit'),
	re_path('literature/details(?:/(?P<pk>\d+))?/$', LiteratureDetails.as_view(), name='literature_details'),
	re_path('literature/list/$', LiteratureList.as_view(), name='literature_list'),

	re_path('person/edit(?:/(?P<pk>\d+))?/$', PersonEdit.as_view(), name='person_edit'),
	re_path('person/details(?:/(?P<pk>\d+))?/$', PersonDetails.as_view(), name='person_details'),
	re_path('person/list/$', PersonList.as_view(), name='person_list'),

	re_path('purpose/edit(?:/(?P<pk>\d+))?/$', PurposeEdit.as_view(), name='purpose_edit'),
	re_path('purpose/details(?:/(?P<pk>\d+))?/$', PurposeDetails.as_view(), name='purpose_details'),
	re_path('purpose/list/$', PurposeList.as_view(), name='purpose_list'),

	re_path('system/edit(?:/(?P<pk>\d+))?/$', SystemEdit.as_view(), name='system_edit'),
	re_path('system/details(?:/(?P<pk>\d+))?/$', SystemDetails.as_view(), name='system_details'),
	re_path('system/list/$', SystemList.as_view(), name='system_list'),

	re_path('religion/edit(?:/(?P<pk>\d+))?/$', ReligionEdit.as_view(), name='religion_edit'),
	re_path('religion/details(?:/(?P<pk>\d+))?/$', ReligionDetails.as_view(), name='religion_details'),
	re_path('religion/list/$', ReligionList.as_view(), name='religion_list'),

	re_path('location/edit(?:/(?P<pk>\d+))?/$', LocationEdit.as_view(), name='location_edit'),
	re_path('location/details(?:/(?P<pk>\d+))?/$', LocationDetails.as_view(), name='location_details'),
	re_path('location/list/$', LocationList.as_view(), name='location_list'),

    # ================ Helper views for types =====================================================
	re_path('eventtype/edit(?:/(?P<pk>\d+))?/$', EventTypeEdit.as_view(), name='eventtype_edit'),
	re_path('eventtype/details(?:/(?P<pk>\d+))?/$', EventTypeDetails.as_view(), name='eventtype_details'),
	re_path('eventtype/list/$', EventTypeList.as_view(), name='eventtype_list'),

	re_path('texttype/edit(?:/(?P<pk>\d+))?/$', TextTypeEdit.as_view(), name='texttype_edit'),
	re_path('texttype/details(?:/(?P<pk>\d+))?/$', TextTypeDetails.as_view(), name='texttype_details'),
	re_path('texttype/list/$', TextTypeList.as_view(), name='texttype_list'),

	re_path('institutiontype/edit(?:/(?P<pk>\d+))?/$', InstitutionTypeEdit.as_view(), name='institutiontype_edit'),
	re_path('institutiontype/details(?:/(?P<pk>\d+))?/$', InstitutionTypeDetails.as_view(), name='institutiontype_details'),
	re_path('institutiontype/list/$', InstitutionTypeList.as_view(), name='institutiontype_list'),

	re_path('eventrole/edit(?:/(?P<pk>\d+))?/$', EventRoleEdit.as_view(), name='eventrole_edit'),
	re_path('eventrole/details(?:/(?P<pk>\d+))?/$', EventRoleDetails.as_view(), name='eventrole_details'),
	re_path('eventrole/list/$', EventRoleList.as_view(), name='eventrole_list'),

	re_path('personsymbol/edit(?:/(?P<pk>\d+))?/$', PersonSymbolEdit.as_view(), name='personsymbol_edit'),
	re_path('personsymbol/details(?:/(?P<pk>\d+))?/$', PersonSymbolDetails.as_view(), name='personsymbol_details'),
	re_path('personsymbol/list/$', PersonSymbolList.as_view(), name='personsymbol_list'),

	re_path('persontype/edit(?:/(?P<pk>\d+))?/$', PersonTypeEdit.as_view(), name='persontype_edit'),
	re_path('persontype/details(?:/(?P<pk>\d+))?/$', PersonTypeDetails.as_view(), name='persontype_details'),
	re_path('persontype/list/$', PersonTypeList.as_view(), name='persontype_list'),

    # ================ CMS ========================================================================
    re_path(r'^cpage/list', CpageListView.as_view(), name='cpage_list'),
    re_path(r'^cpage/details(?:/(?P<pk>\d+))?/$', CpageDetails.as_view(), name='cpage_details'),
    re_path(r'^cpage/edit(?:/(?P<pk>\d+))?/$', CpageEdit.as_view(), name='cpage_edit'),
    re_path(r'^cpage/clocation/add(?:/(?P<pk>\d+))?/$', CpageAdd.as_view(), name='cpage_add_loc'),

    re_path(r'^clocation/list', ClocationListView.as_view(), name='clocation_list'),
    re_path(r'^clocation/details(?:/(?P<pk>\d+))?/$', ClocationDetails.as_view(), name='clocation_details'),
    re_path(r'^clocation/edit(?:/(?P<pk>\d+))?/$', ClocationEdit.as_view(), name='clocation_edit'),
    re_path(r'^clocation/citem/add(?:/(?P<pk>\d+))?/$', ClocationAdd.as_view(), name='clocation_add_item'),

    re_path(r'^citem/list', CitemListView.as_view(), name='citem_list'),
    re_path(r'^citem/details(?:/(?P<pk>\d+))?/$', CitemDetails.as_view(), name='citem_details'),
    re_path(r'^citem/edit(?:/(?P<pk>\d+))?/$', CitemEdit.as_view(), name='citem_edit'),
    re_path(r'^citem/safe(?:/(?P<pk>\d+))?/$', CitemSafe.as_view(), name='citem_safe'),
    re_path(r'^citem/settings', csettings, name='citem_settings'),

    re_path(r'^chelp/list', ChelpListView.as_view(), name='chelp_list'),
    re_path(r'^chelp/details(?:/(?P<pk>\d+))?/$', ChelpDetails.as_view(), name='chelp_details'),
    re_path(r'^chelp/edit(?:/(?P<pk>\d+))?/$', ChelpEdit.as_view(), name='chelp_edit'),

    # Other stuff from EK
    re_path(r'^nlogin', nlogin, name='nlogin'),
    path('register', RegisterView.as_view(), name='signup'),
    re_path(r'^login/user/(?P<user_id>\w[\w\d_\-]+)$', login_as_user, name='login_as'),

]

if settings.DEBUG:
    print('debug')
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL,
        document_root= settings.MEDIA_ROOT)
else:
    print('live')
    x = re_path(r'media/(?P<filename>.*)$', views.protected_media,
        name='protected_media')
    urlpatterns.append(x)