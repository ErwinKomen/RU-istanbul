"""
Views for the installations app
"""
from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect
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
from .forms import EventTypeForm, TextTypeForm, InstallationTypeForm
from .forms import partial_year_to_date
from utilities.views import edit_model
# EK: adding detail views
from basic.utils import ErrHandle
from basic.views import BasicDetails, add_rel_item, get_current_datetime, get_application_context
from cms.views import add_cms_contents

# @permission_required('utilities.add_generic')
def home(request):
    """Renders the home page."""

    assert isinstance(request, HttpRequest)
    response = "-"
    oErr = ErrHandle()
    try:
        # Set the template
        template = "installations/home.html"

        # Get the image information
        f = 'Panorama of Constantinople, detail showing the Valens aqueduct'
        image = Image.objects.get(title = f)

        # Retrieve the moderator-specified introductin text
        home_intro = ""

        # Prepare the context
        context = { 'title': 'Istanbul-su', 
                    'image':image,
                    'home_intro': home_intro }
        context = get_application_context(request, context)

        # Add context items from the CMS system
        context = add_cms_contents('home', context)

        # Show the home page
        response = render(request,template,context)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("installations/home")
        response = msg
    return response

def nlogin(request):
    """Renders the not-logged-in page."""
    assert isinstance(request, HttpRequest)
    context =  {    'title':    'Not logged in', 
                    'message':  'Radboud University istanbul-su utility.',
                    'year':     timezone.now().year,}
    context['is_app_uploader'] = False
    return render(request,'basic/basic_nlogin.html', context)

def login_as_user(request, user_id):
    assert isinstance(request, HttpRequest)

    # Find out who I am
    supername = request.user.username
    super = User.objects.filter(username__iexact=supername).first()
    if super == None:
        return nlogin(request)

    # Make sure that I am superuser
    if super.is_staff and super.is_superuser:
        user = User.objects.filter(username__iexact=user_id).first()
        if user != None:
            # Perform the login
            login(request, user)
            return HttpResponseRedirect(reverse("installations:home"))

    return home(request)

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    response = "-"
    oErr = ErrHandle()
    try:
        template = "installations/contact.html"
        context = dict(
            page_name="Contact",
            title="Contact",
            message="Mariëtte Verhoeven",
            year=get_current_datetime().year
            )
        context = get_application_context(request, context)
        response = render(request, template, context)
    except:
        msg = oErr.get_error_message()
        oErr.DoError("installations/contact")
        response = msg
    return response


# --------------------- System ----------------------------------------------
def edit_system(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [System] instance"""

    names = 'systeminstallation_formset'
    return edit_model(request, __name__, 'System','installations',pk,
        formset_names = names, focus = focus, view = view)

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

# --------------------- Installation Type ------------------------------------
def edit_installationtype(request, pk = None, focus = '', view = 'complete'):
    """Allow adding a new or editing an existing [Installation type] instance"""

    names = ''
    return edit_model(request, __name__, 'InstallationType','installations',pk,
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
