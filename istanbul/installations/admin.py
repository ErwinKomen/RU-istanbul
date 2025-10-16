from django.contrib import admin


# From own application
from istanbul.settings import ADMIN_SITE_URL
from installations.models import *


# Register your models here.
admin.site.register(LocType)
admin.site.register(InstallationStatus)
admin.site.register(DateType)

# Register link
admin.site.site_url = ADMIN_SITE_URL
