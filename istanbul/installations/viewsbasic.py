"""
Views for the installations app - based on the 'basic' app
"""

from django.db.models import Q, Prefetch, Count, F
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _, gettext_lazy
import copy

# From own applicatino
from .models import System, Image, Installation, SystemInstallationRelation
from .models import InstallationType, Purpose
from .models import Event, EventLiteratureRelation, Literature
from .models import Person, EventPersonRelation
from .models import Institution, EventInstitutionRelation
from .forms import SystemForm, PersonForm, InstallationForm, InstallationSearchForm
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
from basic.views import BasicDetails, BasicList, add_rel_item, get_current_datetime
from mapview.views import MapView



# --------------------- Purpose ----------------------------------------------

class EventEdit(BasicDetails):
    """Simple view mode of [Event]"""

    model = Event
    mForm = EventForm
    prefix = "evt"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Event', 'app_name': 'installations' })
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'name',          'value': instance.name                      },
                {'type': 'plain', 'label': 'event type',    'value': instance.get_value('eventtype')    },
                {'type': 'plain', 'label': 'start date',    'value': instance.get_value('startdate')    },
                {'type': 'plain', 'label': 'end date',      'value': instance.get_value('enddate')      },
                {'type': 'plain', 'label': 'date comments', 'value': instance.date_comments             },
                {'type': 'plain', 'label': 'installations', 'value': instance.get_value('installations')},
                {'type': 'plain', 'label': 'persons',       'value': instance.get_value('persons')      },
                {'type': 'plain', 'label': 'description',   'value': instance.description               },
                {'type': 'plain', 'label': 'comments',      'value': instance.comments                  },
            ]
            context['title'] = "View Event"
            context['editview'] = reverse("installations:edit_event", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventDetails/add_to_context")

        # Return the context we have made
        return context


class EventDetails(EventEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(EventDetails, self).add_to_context(context, instance)

        oErr = ErrHandle()
        bShowPersons = False
        bShowInstallations = False
        try:
            # Lists of related objects
            related_objects = []

            resizable = True
            index = 1 
            sort_start = '<span class="sortable"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_start_int = '<span class="sortable integer"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_start_mix = '<span class="sortable mixed"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_end = '</span>'

            # ============ List of Literature that links to this Event ===========================================
            literatures = dict(title="Literature connected to this Event", prefix="litr", 
                               classes="collapse", label="Literature")
            if resizable: literatures['gridclass'] = "resizable"

            rel_list = []
            qs = EventLiteratureRelation.objects.filter(event=instance, literature__isnull=False).order_by('literature__code')
            for item in qs:
                literature = item.literature
                url = reverse("literature_details", kwargs={'pk': literature.id})
                # url_relation = reverse("eventliterature_details", kwargs={'pk': item.id})
                url_relation = None
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Code for this literature
                add_rel_item(rel_item, literature.code, False, main=False, nowrap=False, link=url)

                # Page number of this code
                add_rel_item(rel_item, item.page_number, False, main=False, nowrap=True, link=url_relation)

                ## Title of literature
                #add_rel_item(rel_item, literature.title, False, main=False, nowrap=False, link=url)

                # Excerpt on literature page
                add_rel_item(rel_item, item.text, False, main=False, nowrap=False, link=url_relation)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            literatures['rel_list'] = rel_list

            literatures['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Code</span>{}'.format(sort_start, sort_end), 
                '{}<span>Page</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Excerpt</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(literatures)

            # ============ List of Persons that links to this Event ===========================================
            if bShowPersons:
                persons = dict(title="Persons connected to this Event", prefix="pers", label="Persons", classes="collapse")
                if resizable: persons['gridclass'] = "resizable"

                rel_list = []
                index = 1 
                qs = EventPersonRelation.objects.filter(event=instance, person__isnull=False).order_by('person__name')
                for item in qs:
                    person = item.person
                    url = reverse("person_details", kwargs={'pk': person.id})
                    # url_relation = reverse("eventperson_details", kwargs={'pk': item.id})
                    url_relation = None
                    rel_item = []
                
                    # Order number for this item
                    add_rel_item(rel_item, index, False, align="right")
                    index += 1

                    # Name for this literature
                    add_rel_item(rel_item, person.name, False, main=True, nowrap=True, link=url)

                    # Role for this person / event relation
                    add_rel_item(rel_item, item.role.name, False, main=False, nowrap=True, link=url_relation)

                    # Add this line to the list
                    rel_list.append(dict(id=item.id, cols=rel_item))

                persons['rel_list'] = rel_list

                persons['columns'] = [
                    '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                    '{}<span>Name</span>{}'.format(sort_start, sort_end), 
                    '{}<span>Role</span>{}'.format(sort_start, sort_end), 
                    ]
                related_objects.append(persons)

            # ============ List of Institutions that links to this Event ===========================================
            institutions = dict(title="Institutions connected to this Event", prefix="instit", label="Institutions", classes="collapse")
            if resizable: institutions['gridclass'] = "resizable"

            rel_list = []
            index = 1 
            qs = EventInstitutionRelation.objects.filter(event=instance, institution__isnull=False).order_by('institution__english_name')
            for item in qs:
                institution = item.institution
                url = reverse("institution_details", kwargs={'pk': institution.id})
                # url_relation = reverse("eventinstitution_details", kwargs={'pk': item.id})
                url_relation = None
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Name for this institution (English)
                add_rel_item(rel_item, institution.english_name, False, main=True, nowrap=True, link=url)

                # Role for this institution / event relation
                add_rel_item(rel_item, item.get_value('role'), False, main=False, nowrap=True, link=url_relation)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            institutions['rel_list'] = rel_list

            institutions['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Name</span>{}'.format(sort_start, sort_end), 
                '{}<span>Role</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(institutions)

            # Add all related objects to the context
            context['related_objects'] = related_objects

            # ============ List of Installations that links to this Event ===========================================
            if bShowInstallations:
                installations = dict(title="Installations connected to this Event", prefix="instal", label="Installations", classes="collapse")
                if resizable: installations['gridclass'] = "resizable"

                rel_list = []
                index = 1 
                qs = instance.installation_set.all().order_by('english_name')
                for item in qs:
                    installation = item
                    url = reverse("installation_details", kwargs={'pk': installation.id})
                    # url_relation = reverse("eventinstallation_details", kwargs={'pk': item.id})
                    url_relation = None
                    rel_item = []
                
                    # Order number for this item
                    add_rel_item(rel_item, index, False, align="right")
                    index += 1

                    # Name of installation (English)
                    add_rel_item(rel_item, installation.english_name, False, main=True, nowrap=False, link=url)

                    # Still exists
                    add_rel_item(rel_item, installation.get_value('stillexists'), False, main=False, nowrap=True, link=url)

                    # Installation type
                    add_rel_item(rel_item, installation.get_value('instaltype'), False, main=False, nowrap=True, link=url)

                    # Systems
                    add_rel_item(rel_item, installation.get_value('systems'), False, main=False, nowrap=True, link=url)

                    # Add this line to the list
                    rel_list.append(dict(id=item.id, cols=rel_item))

                installations['rel_list'] = rel_list

                installations['columns'] = [
                    '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                    '{}<span>Installation</span>{}'.format(sort_start, sort_end), 
                    '{}<span>Still exists</span>{}'.format(sort_start_int, sort_end), 
                    '{}<span>Type</span>{}'.format(sort_start_int, sort_end), 
                    '{}<span>Systems</span>{}'.format(sort_start, sort_end), 
                    ]
                related_objects.append(installations)

            # Add all related objects to the context
            context['related_objects'] = related_objects

            # ============================ END OF RELATED OBJECTS ================================================

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
            lHtml.append(render_to_string('installations/event_addition.html', context, self.request))
            context['after_details'] = "\n".join(lHtml)
                

        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventDetails/add_to_context")

        # Return the context we have made
        return context


# --------------------- Image ----------------------------------------

class ImageEdit(BasicDetails):
    """Simple view mode of [System]"""

    model = Image
    mForm = ImageForm
    prefix = "img"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Image', 'app_name': 'installations' })
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'title',             'value': instance.get_label()   },
                {'type': 'plain', 'label': 'maker',             'value': instance.maker         },
                {'type': 'plain', 'label': 'url',               'value': instance.url           },
                {'type': 'plain', 'label': 'year',              'value': instance.year          },
                {'type': 'plain', 'label': 'current location',  'value': instance.current_location      },
                {'type': 'plain', 'label': 'coordinate',        'value': instance.get_value('coordinate')},
                {'type': 'plain', 'label': 'description',       'value': instance.description   },
                {'type': 'plain', 'label': 'comments',          'value': instance.comments      },
                # {'type': 'plain', 'label': 'systems',           'value': instance.get_value('systems')      },
            ]
            context['title'] = "View Image"
            context['editview'] = reverse("installations:edit_image", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("ImageDetails/add_to_context")

        # Return the context we have made
        return context


class ImageDetails(ImageEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context
        context = super(ImageDetails, self).add_to_context(context, instance)

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

            # List of Events that link to this Image
            events = dict(title="Events connected to this Image", prefix="evnt", 
                          classes="collapse",label="Events")
            if resizable: events['gridclass'] = "resizable"

            rel_list = []
            qs = instance.event_set.all().order_by('start_date', 'end_date', 'name')
            for item in qs:
                event = item
                url = reverse("event_details", kwargs={'pk': event.id})
                # url_relation = reverse("eventperson_details", kwargs={'pk': item.id})
                url_relation = None
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Name of event
                add_rel_item(rel_item, event.name, False, main=True, nowrap=False, link=url)

                # start date
                add_rel_item(rel_item, event.get_value('startdate'), False, main=False, nowrap=True, link=url)

                # end date
                add_rel_item(rel_item, event.get_value('enddate'), False, main=False, nowrap=True, link=url)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            events['rel_list'] = rel_list

            events['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Event</span>{}'.format(sort_start, sort_end), 
                '{}<span>Start date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>End date date</span>{}'.format(sort_start_int, sort_end), 
                ]
            related_objects.append(events)

            # List of Installations that link to this Image
            installations = dict(title="Installations connected to this Image", prefix="inst",
                            classes="collapse", label="Installations")
            if resizable: installations['gridclass'] = "resizable"

            rel_list = []
            qs = instance.installation_set.all().order_by('english_name')
            for item in qs:
                installation = item
                url = reverse("installation_details", kwargs={'pk': installation.id})
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Name of installation
                add_rel_item(rel_item, installation.english_name, False, main=True, nowrap=False, link=url)

                # Still exists
                add_rel_item(rel_item, installation.get_value('stillexists'), False, main=False, nowrap=True, link=url)

                # Installation type
                add_rel_item(rel_item, installation.get_value('instaltype'), False, main=False, nowrap=True, link=url)

                # Systems
                add_rel_item(rel_item, installation.get_value('systems'), False, main=False, nowrap=True, link=url)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            installations['rel_list'] = rel_list

            installations['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Installation</span>{}'.format(sort_start, sort_end), 
                '{}<span>Still exists</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Type</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Systems</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(installations)

            # Add all related objects to the context
            context['related_objects'] = related_objects

            # ====================== After Details: image ==========================================
            lHtml = []
            if 'after_details' in context:
                lHtml.append(context['after_details'])

            # Note: there is only one image
            img_html, sTitle = instance.get_image_html()
            oImage = dict(img=img_html, title=sTitle, info=sTitle)
            context['default'] = oImage
            context['pictures'] = []

            # COmbine and show the additions
            lHtml.append(render_to_string('installations/image_addition.html', context, self.request))
            context['after_details'] = "\n".join(lHtml)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("ImageDetails/add_to_context")

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
                {'type': 'plain', 'label': 'event persons', 'value': instance.get_value('eventpersons')  },
                {'type': 'plain', 'label': 'purposes',      'value': instance.get_value('purposes')},
                {'type': 'plain', 'label': 'still exists',  'value': instance.get_value('stillexists') },
                {'type': 'plain', 'label': 'type',          'value': instance.get_value('instaltype')    },
                # {'type': 'plain', 'label': 'images',        'value': instance.get_value('images')  },
                {'type': 'plain', 'label': 'description',   'value': instance.description   },
                {'type': 'plain', 'label': 'comments',      'value': instance.comments      },
                {'type': 'plain', 'label': 'systems',       'value': instance.get_value('systems') },
            ]
            context['title'] = "View Installation"
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


class InstallationList(BasicList):
    """List and search view for Installation"""

    model = Installation 
    listform = InstallationSearchForm
    prefix = "inst"
    has_select2 = True
    sg_name = "Installation"        # This is the name as it appears e.g. in "Add a new XXX" (in the basic listview)
    plural_name = "Installations"   # As displayed
    new_button = False              # Normally this is false, unless this is someone with editing rights
    order_cols = ['english_name', 'installation_type__name', '', '', '']
    order_default = order_cols
    order_heads = [
        {'name': 'Name',        'order': 'o=1', 'type': 'str', 'custom': 'instalname',  'linkdetails': True,  'main': True},
        {'name': 'Type',        'order': 'o=2', 'type': 'str', 'custom': 'instaltype'               },
        {'name': 'Purposes',    'order': '',    'type': 'str', 'custom': 'purposes'                 },
        {'name': 'Persons',     'order': '',    'type': 'str', 'custom': 'evpersons',   'allowwrap': True},
        {'name': 'Events',      'order': '',    'type': 'str', 'custom': 'events',      'allowwrap': True},
        ]
                   
    filters = [ 
        {"name": "Name",            "id": "filter_name",    "enabled": False},
        {"name": "Type",            "id": "filter_itype",   "enabled": False},
        {"name": "Purpose",         "id": "filter_purpose", "enabled": False},
        {"name": "Person",          "id": "filter_person",  "enabled": False},
        {"name": "Event",           "id": "filter_event",   "enabled": False},
        ]
    searches = [
        {'section': '', 'filterlist': [
            {'filter': 'name',      'dbfield': 'english_name',      'keyS': 'english_name'},
            {'filter': 'itype',     'fkfield': 'installation_type', 'keyFk': 'name', 'keyList': 'itypelist',    'infield': 'name'},
            {'filter': 'purpose',   'fkfield': 'purposes',          'keyFk': 'name', 'keyList': 'purplist',     'infield': 'name'},
            {'filter': 'person',    'fkfield': 'events__eventpersonrelations__person',   
                                                                    'keyFk': 'name', 'keyList': 'perslist',     'infield': 'name'},
            {'filter': 'event',     'fkfield': 'events',            'keyFk': 'name', 'keyList': 'eventlist',    'infield': 'name'},
            ]
         } 
        ] 

    def get_field_value(self, instance, custom):
        """Define what is actually displayed"""

        sBack = ""
        sTitle = ""
        html = []
        oErr = ErrHandle()
        try:
            if custom == "saved":
                # Get the correctly visible date
                sBack = instance.get_saved()

            elif custom == "instalname":
                # Get the correctly visible date
                sBack = instance.get_value("name")

            elif custom == "instaltype":
                sBack = instance.get_value("instaltype")

            elif custom == "purposes":
                sBack = instance.get_value("purposes")

            elif custom == "evpersons":
                sBack = instance.get_value("eventpersons", options={'skiprole': True})

            elif custom == "events":
                sBack = instance.get_value("events", ", ", options={'skipname': instance.english_name})
            
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationList/get_field_value")

        return sBack, sTitle

    def add_to_context(self, context, initial):
        """Additional details that have to do with the mapview"""

        oErr = ErrHandle()
        try:
            # All people (including non-users) should see the listview
            context['authenticated'] = True

            # Provide the link to the mapview url
            context['mapviewurl'] = reverse('installation_map')
            # Signal that 'basicmap' should be used (used in `basic_list.html`)
            context['basicmap'] = True

            # Figure out how many locations there are
            lst_installations = self.qs.values('id')
            sLocationCount = Image.objects.filter(installation__in=lst_installations).order_by('id').distinct().count()
            context['mapcount'] = sLocationCount

        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationList/add_to_context")
        return context


class InstallationMap(MapView):
    """Mapview that leans on the InstallationList listview"""

    model = Installation    # This is the basic model of the related listview
    modEntry = Image        # Each point on the map is a Location of which an image exists
    use_object = False      # We are **not** grouping around one language
    prefix = "map"          # Needs to differ from the ``InstallationList`` prefix
    param_list = ""
    frmSearch = InstallationSearchForm

    def initialize(self):
        super(InstallationMap, self).initialize()

        oErr = ErrHandle()
        try:
            # Entries with a 'form' value
            self.entry_list = []

            # Get the location's details: name, id, x-coordinate, y-coordinate
            self.add_entry('locname',       'str', 'title')
            self.add_entry('location_id',   'str', 'id')
            # labels 'point_x' and 'point_y' must be used for the coordinates
            self.add_entry('point_x',       'str', 'latitude')
            self.add_entry('point_y',       'str', 'longitude')
            # The key grouping elements for this image location
            self.add_entry('trefwoord',     'str', 'installation__still_exists')
            self.add_entry('info',          'str', 'title')

            # Get a version of the current listview
            lv = InstallationList()
            lv.initializations()
            # Get the list of [Installation] elements
            qs_installation = lv.get_queryset(self.request)
            # Figure out what the list of installations will be
            lst_installation = qs_installation.values('id')

            # Get a full queryset of the images for these installations
            qs_loc = Image.objects.filter(Q(installation__in=lst_installation))

            # Essential: make sure that self.qs gets filled
            self.qs = qs_loc

        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationMap/initialize")
        return None

    def group_entries(self, lst_this):
        """Allow changing the list of entries"""

        oErr = ErrHandle()
        exclude_fields = ['point', 'point_x', 'point_y', 'pop_up', 'locatie', 'country', 'city']
        try:

            # We need to create a new list, based on the 'point' parameter
            set_point = {}
            for oEntry in lst_this:
                # Regular stuff
                point = oEntry['point']
                if not point in set_point:
                    # Create a new entry
                    set_point[point] = dict(
                        count=0, items=[], point=point,
                        trefwoord=str(oEntry['trefwoord']),
                        locatie=oEntry['locname'],
                        locid=oEntry['location_id'],
                        info=oEntry['info']
                        )
                # Retrieve the item from the set
                oPoint = set_point[point]
                # Add this entry
                oPoint['count'] += 1
                oPoint['items'].append( { k:v for k,v in oEntry.items() if not k in exclude_fields } )

            # Review them again
            lst_back = []
            for point, oEntry in set_point.items():
                # Create the popup
                oEntry['pop_up'] = self.get_group_popup(oEntry)
                # Add it to the list we return
                lst_back.append(oEntry)

            total_count = len(lst_back)
            # Return the new list
            lst_this = copy.copy(lst_back)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationMap/group_entries")

        return lst_this

    def get_group_popup(self, oPoint):
        """Create a popup from the 'key' values defined in [initialize()]"""

        oErr = ErrHandle()
        pop_up = ""
        try:
            # Figure out what the link would be to this list of items
            url = reverse('image_details', kwargs={'pk': oPoint['locid']})
            # Create the popup
            pop_up = '<p class="h4" title="{}">{}</p>'.format(oPoint['locatie'], oPoint['locatie'][:20])
            pop_up += '<hr style="border: 1px solid green" />'
            popup_title_1 = _("Show")
            popup_title_2 = _("objects in the list")
            sLanguage = "exists" if oPoint['trefwoord'] == "True" else "extinct"
            pop_up += '<p style="font-size: large;"><a href="{}" title="{} {} {}"><span style="color: purple;">{}</span> in: {} {}</a></p>'.format(
                url, popup_title_1, oPoint['count'],popup_title_2, oPoint['count'], oPoint['trefwoord'], sLanguage)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationMap/get_group_popup")
        return pop_up



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
            context['editview'] = reverse("installations:edit_installationtype", kwargs={'pk': instance.id})
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


# --------------------- Institution ----------------------------------------

class InstitutionEdit(BasicDetails):
    """Simple view mode of [System]"""

    model = Institution
    mForm = InstitutionForm
    prefix = "inst"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Institution', 'app_name': 'installations' })
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'english name',      'value': instance.english_name  },
                {'type': 'plain', 'label': 'turkish name',      'value': instance.turkish_name  },
                {'type': 'plain', 'label': 'original name',     'value': instance.original_name },
                {'type': 'plain', 'label': 'ottoman name',      'value': instance.ottoman_name  },
                {'type': 'plain', 'label': 'institution type',  'value': instance.get_value('instittype')    },
                {'type': 'plain', 'label': 'religion',          'value': instance.get_value('religion')  },

                {'type': 'plain', 'label': 'description',       'value': instance.description   },
                {'type': 'plain', 'label': 'comments',          'value': instance.comments      },
            ]
            context['title'] = "View Institution"
            context['editview'] = reverse("installations:edit_institution", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstitutionDetails/add_to_context")

        # Return the context we have made
        return context


class InstitutionDetails(InstitutionEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(InstitutionDetails, self).add_to_context(context, instance)

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

            # List of Events that link to this Institution
            events = dict(title="Events connected to this Institution", prefix="evnt")
            if resizable: events['gridclass'] = "resizable"

            rel_list = []
            qs = EventInstitutionRelation.objects.filter(institution=instance, event__isnull=False).order_by(
                    'event__start_date', 'event__end_date', 'event__name')
            for item in qs:
                event = item.event
                url = reverse("event_details", kwargs={'pk': event.id})
                # url_relation = reverse("eventinstitution_details", kwargs={'pk': item.id})
                url_relation = None
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Name of event
                add_rel_item(rel_item, event.name, False, main=True, nowrap=False, link=url)

                # start date
                add_rel_item(rel_item, event.get_value('startdate'), False, main=False, nowrap=True, link=url)

                # end date
                add_rel_item(rel_item, event.get_value('enddate'), False, main=False, nowrap=True, link=url)

                # Institution's role in this event
                add_rel_item(rel_item, item.get_value('role'), False, main=False, nowrap=True, link=url_relation)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            events['rel_list'] = rel_list

            events['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Event</span>{}'.format(sort_start, sort_end), 
                '{}<span>Start date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>End date date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Institution role</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(events)

            # Add all related objects to the context
            context['related_objects'] = related_objects
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstitutionDetails/add_to_context")

        # Return the context we have made
        return context


# --------------------- Literature ------------------------------------

class LiteratureEdit(BasicDetails):
    """Simple view mode of [Literature]"""

    model = Literature
    mForm = LiteratureForm
    prefix = "lit"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={
            'model_name': 'Literature', 'app_name': 'installations'})
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'code',          'value': instance.code          },
                {'type': 'plain', 'label': 'title',         'value': instance.title         },
                {'type': 'plain', 'label': 'description',   'value': instance.description   },
                {'type': 'plain', 'label': 'comments',      'value': instance.comments      },
            ]
            context['title'] = "View literature"
            context['editview'] = reverse("installations:edit_literature", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("LiteratureDetails/add_to_context")

        # Return the context we have made
        return context


class LiteratureDetails(LiteratureEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(LiteratureDetails, self).add_to_context(context, instance)

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

            # List of Events that link to this Literature
            events = dict(title="Connections to this Literature", prefix="evnt")
            if resizable: events['gridclass'] = "resizable"

            rel_list = []
            qs = EventLiteratureRelation.objects.filter(literature=instance).exclude(
                    event__isnull=True, text_type__isnull=True).order_by(
                    'event__start_date', 'event__end_date', 'event__name')
            for item in qs:
                event = item.event
                url = None
                if not event is None: 
                    reverse("event_details", kwargs={'pk': event.id})
                # url_relation = reverse("eventperson_details", kwargs={'pk': item.id})
                url_relation = None
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Texttype of relation
                add_rel_item(rel_item, item.get_value('texttype'), False, main=False, nowrap=True, link=url)

                # Name of event
                add_rel_item(rel_item, item.get_value('eventname'), False, main=True, nowrap=False, link=url)

                # start date
                add_rel_item(rel_item, item.get_value('startdate'), False, main=False, nowrap=True, link=url)

                # end date
                add_rel_item(rel_item, item.get_value('enddate'), False, main=False, nowrap=True, link=url)

                # Literature page range
                add_rel_item(rel_item, item.get_value('pages'), False, main=False, nowrap=True, link=url)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            events['rel_list'] = rel_list

            events['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Text type</span>{}'.format(sort_start, sort_end), 
                '{}<span>Event</span>{}'.format(sort_start, sort_end), 
                '{}<span>Start date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>End date date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Pages</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(events)

            # Add all related objects to the context
            context['related_objects'] = related_objects
        except:
            msg = oErr.get_error_message()
            oErr.DoError("LiteratureDetails/add_to_context")

        # Return the context we have made
        return context


# --------------------- Person ----------------------------------------------

class PersonEdit(BasicDetails):
    """Simple view mode of [Person]"""

    model = Person
    mForm = PersonForm
    prefix = "per"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Person', 'app_name': 'installations' })
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'name',          'value': instance.name                  },
                {'type': 'plain', 'label': 'gender',        'value': instance.get_value('gender')   },
                {'type': 'plain', 'label': 'birth year',    'value': instance.birth_year            },
                {'type': 'plain', 'label': 'death year',    'value': instance.death_year            },
                {'type': 'plain', 'label': 'start reign',   'value': instance.start_reign           },
                {'type': 'plain', 'label': 'end reign',     'value': instance.end_reign             },
                {'type': 'plain', 'label': 'religion',      'value': instance.get_value('religion') },

                {'type': 'plain', 'label': 'description',   'value': instance.description           },
                {'type': 'plain', 'label': 'comments',      'value': instance.comments              },
            ]
            context['title'] = "View Person"
            context['editview'] = reverse("installations:edit_person", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("PersonDetails/add_to_context")

        # Return the context we have made
        return context


class PersonDetails(PersonEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(PersonDetails, self).add_to_context(context, instance)

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

            # List of Events that link to this Person
            events = dict(title="Events connected to this Person", prefix="evnt")
            if resizable: events['gridclass'] = "resizable"

            rel_list = []
            qs = EventPersonRelation.objects.filter(person=instance, event__isnull=False).order_by(
                    'event__start_date', 'event__end_date', 'event__name')
            for item in qs:
                event = item.event
                url = reverse("event_details", kwargs={'pk': event.id})
                # url_relation = reverse("eventperson_details", kwargs={'pk': item.id})
                url_relation = None
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Name of event
                add_rel_item(rel_item, event.name, False, main=True, nowrap=False, link=url)

                # start date
                add_rel_item(rel_item, event.get_value('startdate'), False, main=False, nowrap=True, link=url)

                # end date
                add_rel_item(rel_item, event.get_value('enddate'), False, main=False, nowrap=True, link=url)

                # Person's role in this event
                add_rel_item(rel_item, item.get_value('role'), False, main=False, nowrap=True, link=url)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            events['rel_list'] = rel_list

            events['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Event</span>{}'.format(sort_start, sort_end), 
                '{}<span>Start date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>End date date</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Person role</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(events)

            # Add all related objects to the context
            context['related_objects'] = related_objects

        except:
            msg = oErr.get_error_message()
            oErr.DoError("PersonDetails/add_to_context")

        # Return the context we have made
        return context


# --------------------- Purpose ----------------------------------------------

class PurposeEdit(BasicDetails):
    """Simple view mode of [Purpose]"""

    model = Purpose
    mForm = PurposeForm
    prefix = "pur"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Purpose', 'app_name': 'installations' })
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
            context['title'] = "View Purpose"
            context['editview'] = reverse("installations:edit_system", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("PurposeDetails/add_to_context")

        # Return the context we have made
        return context


class PurposeDetails(PurposeEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(PurposeDetails, self).add_to_context(context, instance)

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

            # List of Installations that link to this Purpose
            installations = dict(title="Installations connected to this Purpose", prefix="inst")
            if resizable: installations['gridclass'] = "resizable"

            rel_list = []
            qs = instance.installation_set.all().order_by('english_name')
            for item in qs:
                installation = item
                url = reverse("installation_details", kwargs={'pk': installation.id})
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Name of installation
                add_rel_item(rel_item, installation.english_name, False, main=True, nowrap=False, link=url)

                # Still exists
                add_rel_item(rel_item, installation.get_value('stillexists'), False, main=False, nowrap=True, link=url)

                # Installation type
                add_rel_item(rel_item, installation.get_value('instaltype'), False, main=False, nowrap=True, link=url)

                # Systems
                add_rel_item(rel_item, installation.get_value('systems'), False, main=False, nowrap=True, link=url)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            installations['rel_list'] = rel_list

            installations['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Installation</span>{}'.format(sort_start, sort_end), 
                '{}<span>Still exists</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Type</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Systems</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(installations)

            # Add all related objects to the context
            context['related_objects'] = related_objects

        except:
            msg = oErr.get_error_message()
            oErr.DoError("PurposeDetails/add_to_context")

        # Return the context we have made
        return context


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
            context['title'] = "View System"
            context['editview'] = reverse("installations:edit_system", kwargs={'pk': instance.id})
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
            qs = SystemInstallationRelation.objects.filter(
                system=instance, installation__isnull=False).order_by(
                    'start_date', 'end_date', 'installation__english_name')
            for item in qs:
                installation = item.installation
                url = reverse("installation_details", kwargs={'pk': installation.id})
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


