"""
Views for the installations app - based on the 'basic' app
"""

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse

# From own applicatino
from .models import System, Image, Installation, SystemInstallationRelation
from .models import InstallationType
from .forms import SystemForm, PersonForm, InstallationForm 
from .forms import EventForm, LiteratureForm, InstitutionForm
from .forms import ReligionForm, ImageForm, FigureForm, StyleForm
from .forms import systeminstallation_formset, installationsystem_formset
from .forms import eventliterature_formset, literatureevent_formset
from .forms import eventperson_formset, personevent_formset
from .forms import eventinstitution_formset, institutionevent_formset
from .forms import PurposeForm, EventRoleForm, InstitutionTypeForm
from .forms import EventTypeForm, TextTypeForm, InstallationTypeForm
from .forms import partial_year_to_date

# EK: adding detail views
from basic.utils import ErrHandle
from basic.views import BasicDetails, add_rel_item, get_current_datetime



# --------------------- System ----------------------------------------------

class SystemEdit(BasicDetails):
    """Simple view mode of [System]"""

    model = System
    mForm = SystemForm
    prefix = "sys"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'System', 'app_name': 'installations' })
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'english name',  'value': instance.english_name},
                {'type': 'plain', 'label': 'turkish name',  'value': instance.turkish_name},
                {'type': 'plain', 'label': 'original name', 'value': instance.original_name},
                {'type': 'plain', 'label': 'ottoman name',  'value': instance.ottoman_name},
                {'type': 'plain', 'label': 'description',   'value': instance.description},
                {'type': 'plain', 'label': 'comments',      'value': instance.comments},
            ]
            context['title'] = "View system"
        except:
            msg = oErr.get_error_message()
            oErr.DoError("SystemDetails/add_to_context")

        # Return the context we have made
        return context


class SystemDetails(SystemEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(SystemDetails, self).add_to_context(context, instance)

        oErr = ErrHandle()
        try:
                
            # Lists of related objects
            related_objects = []

            resizable = True
            index = 1 
            sort_start = '<span class="sortable"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_start_int = '<span class="sortable integer"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_start_mix = '<span class="sortable mixed"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_end = '</span>'

            # List of Installations that link to this System
            installations = dict(title="Installations connected to this System", prefix="inst")
            if resizable: installations['gridclass'] = "resizable"

            rel_list = []
            qs = SystemInstallationRelation.objects.filter(system=instance, installation__isnull=False).order_by('installation__english_name')
            for item in qs:
                installation = item.installation
                url = reverse("installation_details", kwargs={'pk': item.id})
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Name of installation
                add_rel_item(rel_item, installation.english_name, False, main=True, nowrap=False, link=url)

                # Start date of relation
                add_rel_item(rel_item, item.start_date, False, main=False, nowrap=False, link=url)

                # End date of relation
                add_rel_item(rel_item, item.end_date, False, main=False, nowrap=False, link=url)

                # Part of value
                add_rel_item(rel_item, item.is_part_of, False, main=False, nowrap=False, link=url)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            installations['rel_list'] = rel_list

            installations['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Installation</span>{}'.format(sort_start, sort_end), 
                '{}<span>Start date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>End date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Part of</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(installations)

            # Add all related objects to the context
            context['related_objects'] = related_objects

        except:
            msg = oErr.get_error_message()
            oErr.DoError("SystemDetails/add_to_context")

        # Return the context we have made
        return context


# --------------------- Installation ----------------------------------------

class InstallationEdit(BasicDetails):
    """Simple view mode of [System]"""

    model = Installation
    mForm = InstallationForm
    prefix = "inst"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Installation', 'app_name': 'installations' })
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'english name',  'value': instance.english_name  },
                {'type': 'plain', 'label': 'turkish name',  'value': instance.turkish_name  },
                {'type': 'plain', 'label': 'original name', 'value': instance.original_name },
                {'type': 'plain', 'label': 'ottoman name',  'value': instance.ottoman_name  },
                {'type': 'plain', 'label': 'events',        'value': instance.get_value('events')  },
                {'type': 'plain', 'label': 'purposes',      'value': instance.get_value('purposes')},
                {'type': 'plain', 'label': 'still exists',  'value': instance.get_value('stillexists') },
                {'type': 'plain', 'label': 'type',          'value': instance.get_value('instaltype')    },
                # {'type': 'plain', 'label': 'images',        'value': instance.get_value('images')  },
                {'type': 'plain', 'label': 'description',   'value': instance.description   },
                {'type': 'plain', 'label': 'comments',      'value': instance.comments      },
                {'type': 'plain', 'label': 'systems',       'value': instance.get_value('systems') },
            ]
            context['title'] = "View installation"
            context['editview'] = reverse("installations:edit_installation", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationDetails/add_to_context")

        # Return the context we have made
        return context


class InstallationDetails(InstallationEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(InstallationDetails, self).add_to_context(context, instance)

        oErr = ErrHandle()
        try:
            lHtml = []
            if 'after_details' in context:
                lHtml.append(context['after_details'])

            # Figure out the list of images
            lst_image = []
            for obj in instance.images.all():
                img_html, sTitle = obj.get_image_html()
                lst_image.append(dict(img=img_html, title=sTitle, info=sTitle))
            if len(lst_image) > 0:
                context['default'] = lst_image[0]
            context['pictures'] = lst_image[1:]

            # COmbine and show the additions
            lHtml.append(render_to_string('installations/installation_addition.html', context, self.request))
            context['after_details'] = "\n".join(lHtml)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationDetails/add_to_context")

        # Return the context we have made
        return context


# --------------------- Installation Type ------------------------------------

class InstallationTypeEdit(BasicDetails):
    """Simple view mode of [InstallationType]"""

    model = InstallationType
    mForm = InstallationTypeForm
    prefix = "instyp"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={
            'model_name': 'InstallationType', 'app_name': 'installations'})
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'name',          'value': instance.name},
                {'type': 'plain', 'label': 'description',   'value': instance.description},
                {'type': 'plain', 'label': 'comments',      'value': instance.comments},
            ]
            context['title'] = "View installation type"
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationTypeDetails/add_to_context")

        # Return the context we have made
        return context


class InstallationTypeDetails(InstallationTypeEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(InstallationTypeDetails, self).add_to_context(context, instance)

        oErr = ErrHandle()
        try:
                
            # Lists of related objects
            related_objects = []

            # Add all related objects to the context
            context['related_objects'] = related_objects
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationTypeDetails/add_to_context")

        # Return the context we have made
        return context
