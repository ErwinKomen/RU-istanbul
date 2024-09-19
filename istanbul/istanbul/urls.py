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
from installations.views import nlogin  #, \
#    SystemDetails, SystemEdit, InstallationDetails, InstallationEdit
from installations.viewsbasic import SystemDetails, SystemEdit, \
    InstallationDetails, InstallationEdit, \
    InstallationTypeDetails, InstallationTypeEdit
from accounts.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),
	path('accounts/',include('accounts.urls')),
	path('accounts/',include('django.contrib.auth.urls')),
	path('utilities/',include('utilities.urls')),
	path('installations/',include('installations.urls')),
	re_path(r'^select2/', include('django_select2.urls')),
	path('',include('installations.urls')),

	# ================== Views ===================================
	re_path('system/edit(?:/(?P<pk>\d+))?/$', SystemEdit.as_view(), name='system_edit'),
	re_path('system/details(?:/(?P<pk>\d+))?/$', SystemDetails.as_view(), name='system_details'),

	re_path('installation/edit(?:/(?P<pk>\d+))?/$', InstallationEdit.as_view(), name='installation_edit'),
	re_path('installation/details(?:/(?P<pk>\d+))?/$', InstallationDetails.as_view(), name='installation_details'),

	re_path('instaltype/edit(?:/(?P<pk>\d+))?/$', InstallationTypeEdit.as_view(), name='installationtype_edit'),
	re_path('instaltype/details(?:/(?P<pk>\d+))?/$', InstallationTypeDetails.as_view(), name='installationtype_details'),

    # Other stuff from EK
    re_path(r'^nlogin', nlogin, name='nlogin'),
    path('register', RegisterView.as_view(), name='signup'),
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