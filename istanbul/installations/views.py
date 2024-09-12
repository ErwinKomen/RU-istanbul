"""
Views for the installations app
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone

# From own applicatino
from .models import System, Image, Installation, SystemInstallationRelation
from .forms import SystemForm, PersonForm, InstallationForm 
from .forms import EventForm, LiteratureForm, InstitutionForm
from .forms import ReligionForm, ImageForm, FigureForm, StyleForm
from .forms import systeminstallation_formset, installationsystem_formset
from .forms import eventliterature_formset, literatureevent_formset
from .forms import eventperson_formset, personevent_formset
from .forms import eventinstitution_formset, institutionevent_formset
from .forms import PurposeForm, EventRoleForm, InstitutionTypeForm
from .forms import EventTypeForm, TextTypeForm
from .forms import partial_year_to_date
from utilities.views import edit_model
# EK: adding detail views
from basic.utils import ErrHandle
from basic.views import BasicDetails, add_rel_item, get_current_datetime

@permission_required('utilities.add_generic')
def home(request):
    f = 'Panorama of Constantinople, detail showing the Valens aqueduct'
    image = Image.objects.get(title = f)
    args = {'image':image}
    return render(request,'installations/home.html',args)

def nlogin(request):
    """Renders the not-logged-in page."""
    assert isinstance(request, HttpRequest)
    context =  {    'title':    'Not logged in', 
                    'message':  'Radboud University istanbul-su utility.',
                    'year':     timezone.now().year,}
    context['is_app_uploader'] = False
    return render(request,'basic/basic_nlogin.html', context)

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    response = "no contacts"
    oErr = ErrHandle()
    try:
        template = "installations/contact.html"
        context = dict(
            page_name="Contact",
            title="Contact",
            message="Mariëtte Verhoeven",
            year=get_current_datetime().year
            )
        response = render(request, template, context)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("installations/contact")
    return response


# --------------------- System ----------------------------------------------
def edit_system(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [System] instance"""

    names = 'systeminstallation_formset'
    return edit_model(request, __name__, 'System','installations',pk,
        formset_names = names, focus = focus, view = view)

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
def edit_installation(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Installation] instance"""

    names = 'installationsystem_formset'
    return edit_model(request, __name__, 'Installation','installations',pk,
        formset_names = names, focus = focus, view = view)

def detail_installation_view(request,pk):
    installation= Installation.objects.get(pk = pk)
    events=installation.events.all().order_by('start_date')
    epr = []
    for event in events:
        for x in event.eventpersonrelation_set.all():
            epr.append(x)
    args = {'installation':installation,'events':events,
        'event_person_relation':epr}
    return render(request,'installations/detail_installation_view.html',args)

class InstallationEdit(BasicDetails):
    """Simple view mode of [System]"""

    model = Installation
    mForm = InstallationForm
    prefix = "sys"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Installation', 'app_name': 'installations' })
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
            context['title'] = "View installation"
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationDetails/add_to_context")

        # Return the context we have made
        return context


class InstallationDetails(InstallationEdit):
    rtype = "html"


# --------------------- Person ----------------------------------------------
def edit_person(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Person] instance"""

    def before_save(form, instance):
        # Check whether the date is filled in as a correct four-digit year
        partial_year_to_date(form, instance, "birth_year", "birth_year")
        partial_year_to_date(form, instance, "death_year", "death_year")
        partial_year_to_date(form, instance, "start_reign", "start_reign")
        partial_year_to_date(form, instance, "end_reign", "end_reign")

    names = 'personevent_formset'
    return edit_model(request, __name__, 'Person','installations',pk,
        formset_names = names, focus = focus, view = view, before_save=before_save)

# --------------------- Institution -----------------------------------------
def edit_institution(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Institution] instance"""

    names = 'institutionevent_formset'
    return edit_model(request, __name__, 'Institution','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Purpose ---------------------------------------------
def edit_purpose(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Purpose] instance"""

    names = ''
    return edit_model(request, __name__, 'Purpose','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Institution Type ------------------------------------
def edit_institutiontype(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Institution type] instance"""

    names = ''
    return edit_model(request, __name__, 'InstitutionType','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Event Type ------------------------------------------
def edit_eventtype(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Event type] instance"""

    names = ''
    return edit_model(request, __name__, 'EventType','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Event Role ------------------------------------------
def edit_eventrole(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Event role] instance"""

    names = ''
    return edit_model(request, __name__, 'EventRole','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Religion --------------------------------------------
def edit_religion(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Religion] instance"""

    names = ''
    return edit_model(request, __name__, 'Religion','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Event -----------------------------------------------
def edit_event(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Event] instance"""

    names = 'eventliterature_formset,eventperson_formset,eventinstitution_formset'
    return edit_model(request, __name__, 'Event','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Literature ------------------------------------------
def edit_literature(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Literature] instance"""

    names = 'literatureevent_formset'
    return edit_model(request, __name__, 'Literature','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Text type -------------------------------------------
def edit_texttype(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Text Type] instance"""

    names = ''
    return edit_model(request, __name__, 'TextType','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Image -----------------------------------------------
def edit_image(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Image] instance"""

    names = ''
    return edit_model(request, __name__, 'Image','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Figure ----------------------------------------------
def edit_figure(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Figure] instance"""

    names = ''
    return edit_model(request, __name__, 'Figure','installations',pk,
        formset_names = names, focus = focus, view = view)

# --------------------- Style -----------------------------------------------
def edit_style(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Style] instance"""

    names = ''
    return edit_model(request, __name__, 'Style','installations',pk,
        formset_names = names, focus = focus, view = view)
