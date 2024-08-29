from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from .models import System, Image, Installation
from .forms import SystemForm, PersonForm, InstallationForm 
from .forms import EventForm, LiteratureForm, InstitutionForm
from .forms import ReligionForm, ImageForm, FigureForm, StyleForm
from .forms import systeminstallation_formset, installationsystem_formset
from .forms import eventliterature_formset, literatureevent_formset
from .forms import eventperson_formset, personevent_formset
from .forms import eventinstitution_formset, institutionevent_formset
from .forms import PurposeForm, EventRoleForm, InstitutionTypeForm
from .forms import EventTypeForm, TextTypeForm
from utilities.views import edit_model

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


@permission_required('utilities.add_generic')
def home(request):
    f = 'Panorama of Constantinople, detail showing the Valens aqueduct'
    image = Image.objects.get(title = f)
    args = {'image':image}
    return render(request,'installations/home.html',args)

# Create your views here.
def edit_system(request, pk = None, focus = '', view = 'complete'):
    names = 'systeminstallation_formset'
    return edit_model(request, __name__, 'System','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_installation(request, pk = None, focus = '', view = 'complete'):
    names = 'installationsystem_formset'
    return edit_model(request, __name__, 'Installation','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_person(request, pk = None, focus = '', view = 'complete'):
    names = 'personevent_formset'
    return edit_model(request, __name__, 'Person','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_institution(request, pk = None, focus = '', view = 'complete'):
    names = 'institutionevent_formset'
    return edit_model(request, __name__, 'Institution','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_purpose(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'Purpose','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_institutiontype(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'InstitutionType','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_eventtype(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'EventType','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_eventrole(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'EventRole','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_religion(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'Religion','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_event(request, pk = None, focus = '', view = 'complete'):
    names = 'eventliterature_formset,eventperson_formset,eventinstitution_formset'
    return edit_model(request, __name__, 'Event','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_literature(request, pk = None, focus = '', view = 'complete'):
    names = 'literatureevent_formset'
    return edit_model(request, __name__, 'Literature','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_texttype(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'TextType','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_image(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'Image','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_figure(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'Figure','installations',pk,
        formset_names = names, focus = focus, view = view)

def edit_style(request, pk = None, focus = '', view = 'complete'):
    names = ''
    return edit_model(request, __name__, 'Style','installations',pk,
        formset_names = names, focus = focus, view = view)
