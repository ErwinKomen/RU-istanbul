"""
Views for the installations app - based on the 'basic' app
"""

from django.db.models import Q, Prefetch, Count, F
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext as _, gettext_lazy
import copy
import json

# From own applicatino
from .models import EventInstallationRelation, System, Image, Installation, SystemInstallationRelation
from .models import InstallationType, Purpose
from .models import Event, EventLiteratureRelation, Literature
from .models import Person, EventPersonRelation
from .models import Institution, EventInstitutionRelation
from .models import Location, LocType
from .models import PersonSymbol, PersonType
from .forms import SystemForm, PersonForm, InstallationForm, InstallationSearchForm
from .forms import EventForm, LiteratureForm, InstitutionForm
from .forms import ReligionForm, ImageForm, FigureForm, StyleForm
from .forms import systeminstallation_formset, installationsystem_formset
from .forms import eventliterature_formset, literatureevent_formset
from .forms import eventperson_formset, personevent_formset
from .forms import eventinstitution_formset, institutionevent_formset
from .forms import PurposeForm, EventRoleForm, InstitutionTypeForm
from .forms import EventTypeForm, TextTypeForm, InstallationTypeForm
from .forms import LocationForm, PersonSymbolForm, PersonTypeForm
from .forms import PersonTypeSearchForm, PersonSymbolSearchForm
from .forms import ImageSearchForm
from .forms import ExternalLinkForm, installationextlink_formset
from .forms import EventLiteratureRelationForm
from .forms import partial_year_to_date

# EK: adding detail views
from basic.utils import ErrHandle
from basic.views import BasicDetails, BasicList, add_rel_item, get_current_datetime, get_application_context
from mapview.views import MapView



# --------------------- Event ----------------------------------------------

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
                {'type': 'plain', 'label': 'installation',  'value': instance.get_value('installations')},
                {'type': 'plain', 'label': 'name',          'value': instance.name                      },
                {'type': 'plain', 'label': 'event type',    'value': instance.get_value('eventtype')    },
                {'type': 'plain', 'label': 'start date',    'value': instance.get_value('startdate')    },
                {'type': 'plain', 'label': 'end date',      'value': instance.get_value('enddate')      },
                {'type': 'plain', 'label': 'date comments', 'value': instance.date_comments             },
                {'type': 'plain', 'label': 'persons',       'value': instance.get_value('persons')      },
                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()      },
                {'type': 'plain', 'label': 'comments',      'value': instance.comments                  },
            ]
            context['title'] = "View Event"
            context['editview'] = reverse("installations:edit_event", kwargs={'pk': instance.id})

            # Get the (best candidate for the) related installation
            obj = EventInstallationRelation.objects.filter(event=instance).first()
            if not obj is None:
                installation = obj.installation
                # Get a list of event id's that are 'part of' the related installation
                # idlist = [ x['id'] for x in installation.events.all().values('id')]
                idlist = [ x['id'] for x in installation.events.all().order_by(
                    'start_date', 'end_date', 'name').values('id') ]
                if len(idlist) > 0:
                    # Indicate that we want to see navigation buttons
                    context['navigation_buttons'] = True
                    context['navigate_total'] = len(idlist)
                    context['navigate_current'] = "??"

                    # First and last are easy
                    id_first = idlist[0]
                    id_last = idlist[-1]
                    context['navigate_first'] = "{}".format(reverse('event_details', kwargs={'pk': id_first}) )
                    context['navigate_last'] = "{}".format(reverse('event_details', kwargs={'pk': id_last}) )

                    # Where are we now in the list?
                    id_current = instance.id
                    if id_current in idlist:
                        # Get the index of this id in the idlist
                        idx = idlist.index(id_current)
                        context['navigate_current'] = "{}".format(idx+1)

                        # Okay, now 'previous'...
                        if idx > 0:
                            id_prev = idlist[idx-1]
                            context['navigate_prev'] = "{}".format(reverse('event_details', kwargs={'pk': id_prev}) )

                        # Then what about 'next'...
                        if idx < len(idlist) - 1:
                            id_next = idlist[idx+1]
                            context['navigate_next'] = "{}".format(reverse('event_details', kwargs={'pk': id_next}) )

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
                url_relation = reverse("eventliteraturerelation_details", kwargs={'pk': item.id})
                # url_relation = None
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

            # COmbine and show the additions
            lHtml.append(render_to_string('installations/event_addition.html', context, self.request))
            context['after_details'] = "\n".join(lHtml)
                

        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventDetails/add_to_context")

        # Return the context we have made
        return context


# --------------------- EventLiterature ------------------------------------


class EventLiteratureRelationEdit(BasicDetails):
    """Simple view mode of [EventLiteratureRelation]"""

    model = EventLiteratureRelation
    mForm = EventLiteratureRelationForm
    prefix = "evlit"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={
            'model_name': 'EventLiteratureRelation', 'app_name': 'installations'})
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'page number',   'value': instance.get_value("pages")},
                {'type': 'plain', 'label': 'text type',     'value': instance.get_value("texttype")},
                {'type': 'plain', 'label': 'text',          'value': instance.get_value("text")},
            ]
            context['title'] = "View installation type"
            context['editview'] = reverse("installations:edit_eventliterature", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventLiteratureRelationDetails/add_to_context")

        # Return the context we have made
        return context


class EventLiteratureRelationDetails(EventLiteratureRelationEdit):
    rtype = "html"

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(EventLiteratureRelationDetails, self).add_to_context(context, instance)

        oErr = ErrHandle()
        try:
                
            # Lists of related objects
            related_objects = []

            # Add all related objects to the context
            context['related_objects'] = related_objects
        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventLiteratureRelationDetails/add_to_context")

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
        # self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Image', 'app_name': 'installations' })
        self.listview = reverse('image_list')
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
                # {'type': 'plain', 'label': 'coordinate',        'value': instance.get_value('coordinate')},
                {'type': 'plain', 'label': 'description',       'value': instance.get_description_md()   },
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

    def before_save(self, form, instance):
        """After adding a new Location"""

        bResult = True
        msg = ""
        oErr = ErrHandle()
        try:
            # Try to retrieve the marker location
            image_polygon = self.qd.get("image_polygon")
            if not image_polygon is None and image_polygon != "":
                # This is a stringified json
                oFeature = json.loads(image_polygon)
                # The actual geojson is a bit more complex
                oGeoJson = dict(
                    type="FeatureCollection", name="Unnamed (from map input)", crs=None,
                    features=[ oFeature ]
                )
                # Store the actual object
                form.instance.geojson = oGeoJson
                form.instance.title = "Polygon from map"
        except:
            msg = oErr.get_error_message()
            oErr.DoError("ImageEdit/after_new")
        return bResult, msg


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
            img_html, sTitle = instance.get_image_html(bListGeoJson=True)
            oImage = dict(img=img_html, title=sTitle, info=sTitle, itype=instance.get_itype())
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


class ImageList(BasicList):
    """List and search view for Image"""

    model = Image 
    listform = ImageSearchForm
    prefix = "img"
    has_select2 = True
    sg_name = "Image"               # This is the name as it appears e.g. in "Add a new XXX" (in the basic listview)
    plural_name = "Images"          # As displayed
    new_button = False              # Normally this is false, unless this is someone with editing rights
    fontawesome_already = True      # Already have fontawesome
    order_cols = ['title', 'maker', 'itype__name', 'year', 'current_location']
    order_default = order_cols
    order_heads = [
        {'name': 'title',   'order': 'o=1', 'type': 'str', 'custom': 'title',   'linkdetails': True, 'allowwrap': True}, #, 'main': True},
        {'name': 'maker',   'order': 'o=2', 'type': 'str', 'custom': 'maker',   'linkdetails': True, 'allowwrap': True},
        {'name': 'type',    'order': 'o=3', 'type': 'str', 'custom': 'itype',   'linkdetails': True               },
        {'name': 'year',    'order': 'o=4', 'type': 'int', 'custom': 'year',    'linkdetails': True               },
        {'name': 'location','order': 'o=5', 'type': 'str', 'custom': 'location','linkdetails': True, 'allowwrap': True},
        ]
                   
    filters = [ 
        {"name": "Title",       "id": "filter_title",       "enabled": False},
        {"name": "Maker",       "id": "filter_maker",       "enabled": False},
        {"name": "Image type",  "id": "filter_itype",       "enabled": False},
        {"name": "Year",        "id": "filter_daterange",   "enabled": False},
        {"name": "Location",    "id": "filter_location",    "enabled": False},
        ]
    searches = [
        {'section': '', 'filterlist': [
            {'filter': 'title',         'dbfield': 'title',             'keyS': 'title'},
            {'filter': 'maker',         'dbfield': 'maker',             'keyS': 'maker'},
            {'filter': 'itype',         'fkfield': 'itype',             'keyFk': 'name', 
             'keyList': 'itypelist',    'infield': 'name'},
            {'filter': 'daterange',     'dbfield': 'year__gte',         'keyS': 'start_date'},
            {'filter': 'daterange',     'dbfield': 'year__lte',         'keyS': 'end_date'},
            {'filter': 'location',      'dbfield': 'current_location',  'keyS': 'current_location'},
            ]
         } 
        ] 

    def add_to_context(self, context, initial):
        oErr = ErrHandle()
        try:
            # All people (including non-users) should see the listview
            context['authenticated'] = True

            # Figure out who may edit
            may_add = context['is_app_editor']
            if may_add:
                # Allow creation of new item(s)
                self.new_button = True
                context['new_button'] = self.new_button
                self.basic_add = reverse("installations:add_image")
                context['basic_add'] = self.basic_add
        except:
            msg = oErr.get_error_message()
            oErr.DoError("ImageList/add_to_context")
        return context

    def get_field_value(self, instance, custom):
        """Define what is actually displayed"""

        sBack = ""
        sTitle = ""
        html = []
        oErr = ErrHandle()
        try:
            if custom in ["title", "maker", "itype", "year", "location"]:
                # Get the correctly visible date
                sBack = instance.get_value(custom)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("ImageList/get_field_value")

        return sBack, sTitle


# --------------------- Installation ----------------------------------------

class InstallationEdit(BasicDetails):
    """Simple view mode of [System]"""

    model = Installation
    mForm = InstallationForm
    prefix = "inst"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        # OLD: self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Installation', 'app_name': 'installations' })
        self.listview = reverse('installation_list')
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
                {'type': 'plain', 'label': 'events',        'value': instance.get_value('events')       },
                {'type': 'plain', 'label': 'event persons', 'value': instance.get_value('eventpersons') },
                {'type': 'plain', 'label': 'purposes',      'value': instance.get_value('purposes')     },
                {'type': 'plain', 'label': 'still exists',  'value': instance.get_value('stillexists')  },
                {'type': 'plain', 'label': 'type',          'value': instance.get_value('instaltype')   },
                {'type': 'plain', 'label': 'location',      'value': instance.get_value('location')     },
                # {'type': 'plain', 'label': 'images',        'value': instance.get_value('images')  },
                {'type': 'plain', 'label': 'description',       'value': instance.get_description_md()      },
                {'type': 'plain', 'label': 'comments',          'value': instance.get_comments_md()         },
                {'type': 'plain', 'label': 'systems',           'value': instance.get_value('systems')      },
                # {'type': 'plain', 'label': 'event literature',  'value': instance.get_value('eventliterature')  },
                {'type': 'plain', 'label': 'external',          'value': instance.get_value('extlinks')      },
            ]
            context['title'] = "View Installation"
            context['editview'] = reverse("installations:edit_installation", kwargs={'pk': instance.id})
            # Possible addition, if this item is hidden
            status = instance.installation_status
            if status and status.name == "hide":
                context['title_addition'] = '<span style="font-size: small; color: blue;">(hidden)</span>'

            # Provide the link to the mapview url
            context['mapviewurl'] = reverse('installation_focus_map', kwargs = {"pk": instance.id})
            # Signal that 'basicmap' should be used (used in `basic_list.html`)
            context['basicmap'] = True

            # Figure out how many locations there are
            qs = Installation.objects.all()
            lst_installations = qs.filter(Q(location__isnull=False)).values('id')
            # Also get the number of installations that have a geojson image
            lst_geojson = qs.filter(Q(images__geojson__isnull=False)).values('id')
            sLocationCount = len(lst_installations) + len(lst_geojson)
            context['mapcount'] = sLocationCount
            context['entrycount'] = sLocationCount

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
            # Lists of related objects
            related_objects = []

            resizable = True
            index = 1 
            sort_start = '<span class="sortable"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_start_int = '<span class="sortable integer"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_start_mix = '<span class="sortable mixed"><span class="fa fa-sort sortshow"></span>&nbsp;'
            sort_end = '</span>'

            # ============ List of Literature that links to related events =======================================
            literatures = dict(title="Literature of related events", prefix="litr", 
                               classes="collapse", label="Literature")
            if resizable: literatures['gridclass'] = "resizable"

            rel_list = []
            # Get the literature that is linked to this installation via events
            event_ids = [ x['id'] for x in instance.events.all().values("id") ]
            qs = EventLiteratureRelation.objects.filter(event__id__in=event_ids, 
                    literature__isnull=False).order_by('event__start_date', 'event__end_date', 
                                                       'literature__code', "page_number")
            for item in qs:
                literature = item.literature
                event = item.event
                url = reverse("literature_details", kwargs={'pk': literature.id})
                url_relation = reverse("eventliteraturerelation_details", kwargs={'pk': item.id})
                # url_relation = None
                url_event = reverse('event_details', kwargs={'pk': event.id})
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Event
                label = event.shortlabel()
                # sEvent = "<span class='badge signature gr'><a class='nostyle' href='{}'>{}</a></span>".format(url, label)
                add_rel_item(rel_item, label, False, main=False, nowrap=False, link=url_event)

                # Code for this literature
                add_rel_item(rel_item, literature.code, False, main=False, nowrap=False, link=url)

                # Text type of this literature (primary/secondary)
                sType = item.get_value("texttype")
                add_rel_item(rel_item, sType, False, main=False, nowrap=False, link=url)

                # Page number of this code
                add_rel_item(rel_item, item.page_number, False, main=False, nowrap=True, link=url_relation)

                ## Title of literature
                #add_rel_item(rel_item, literature.title, False, main=False, nowrap=False, link=url)

                # Excerpt on literature page
                add_rel_item(rel_item, item.text, True, main=False, nowrap=False, link=url_relation)

                # Add this line to the list
                rel_list.append(dict(id=item.id, cols=rel_item))

            literatures['rel_list'] = rel_list

            literatures['columns'] = [
                '{}<span>#</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Event</span>{}'.format(sort_start, sort_end), 
                '{}<span>Code</span>{}'.format(sort_start, sort_end), 
                '{}<span>Type</span>{}'.format(sort_start, sort_end), 
                '{}<span>Page</span>{}'.format(sort_start_int, sort_end), 
                '{}<span>Excerpt</span>{}'.format(sort_start, sort_end), 
                ]
            related_objects.append(literatures)

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
                bGeojson = (not obj.geojson is None)
                lst_image.append(dict(img=img_html, title=sTitle, info=sTitle, geojson=bGeojson))
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
    bUseFilter = True
    new_button = False              # Normally this is false, unless this is someone with editing rights
    fontawesome_already = True      # Already have fontawesome
    start_with_list = True          # Start with listview
    order_cols = ['english_name', 'installation_type__name', '', '', '']
    order_default = order_cols
    order_heads = [
        {'name': 'Name',        'order': 'o=1', 'type': 'str', 'custom': 'instalname',  'allowwrap': True, 'linkdetails': True,  'main': True},
        {'name': 'Type',        'order': 'o=2', 'type': 'str', 'custom': 'instaltype'               },
        {'name': 'Purposes',    'order': '',    'type': 'str', 'custom': 'purposes'                 },
        {'name': 'Persons',     'order': '',    'type': 'str', 'custom': 'evpersons',   'allowwrap': True},
        {'name': 'Events',      'order': '',    'type': 'str', 'custom': 'events',      'allowwrap': True},
        ]
                   
    filters = [ 
        {"name": "Name",            "id": "filter_name",        "enabled": False},
        {"name": "Type",            "id": "filter_itype",       "enabled": False},
        {"name": "Purpose",         "id": "filter_purpose",     "enabled": False},
        {"name": "Person",          "id": "filter_person",      "enabled": False},
        {"name": "Event",           "id": "filter_event",       "enabled": False},
        {"name": "System",          "id": "filter_system",      "enabled": False},
        {"name": "Event dates",     "id": "filter_daterange",   "enabled": False},
        {"name": "Status",          "id": "filter_istatus",     "enabled": False, "head_id": True},
        ]
    searches = [
        {'section': '', 'filterlist': [
            {'filter': 'name',      'dbfield': 'english_name',      'keyS': 'english_name'},
            {'filter': 'itype',     'fkfield': 'installation_type', 'keyFk': 'name', 'keyList': 'itypelist',    'infield': 'name'},
            {'filter': 'istatus',   'fkfield': 'installation_status','keyFk': 'name', 'keyList': 'istatuslist', 'infield': 'name'},
            {'filter': 'purpose',   'fkfield': 'purposes',          'keyFk': 'name', 'keyList': 'purplist',     'infield': 'name'},
            {'filter': 'person',    'fkfield': 'events__eventpersonrelations__person',   
             'keyFk': 'name', 'keyList': 'perslist',     'infield': 'name'},
            {'filter': 'daterange', 'dbfield': 'events__start_date__gte',   'keyS': 'start_date'},
            {'filter': 'daterange', 'dbfield': 'events__end_date__lte',     'keyS': 'end_date'},
            {'filter': 'event',     'fkfield': 'events',            'keyFk': 'name', 'keyList': 'eventlist',    'infield': 'name'},
            {'filter': 'system',    'fkfield': 'systeminstallationrelation__system',   
             'keyFk': 'english_name', 'keyList': 'systemlist',   'infield': 'english_name'},
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

            # Hide the 'Status' if this is a non-editor
            is_app_editor = context['is_app_editor']
            for idx, oItem in enumerate(self.filters):
                if oItem['name'] == "Status":
                    # Set or Nullify the [head_id]
                    if is_app_editor:
                        oItem['head_id'] = None
                    else:
                        oItem['head_id'] = True
                    break

            # Provide the link to the mapview url
            context['mapviewurl'] = reverse('installation_map')
            # Signal that 'basicmap' should be used (used in `basic_list.html`)
            context['basicmap'] = True
            context['start_with_list'] = self.start_with_list

            # Figure out how many locations there are
            lst_installations = self.qs.filter(Q(location__isnull=False)).values('id')
            # Also get the number of installations that have a geojson image
            lst_geojson = self.qs.filter(Q(images__geojson__isnull=False)).values('id')
            sLocationCount = len(lst_installations) + len(lst_geojson)
            context['mapcount'] = sLocationCount

            context['fontawesome_already'] = True

        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationList/add_to_context")
        return context

    def adapt_search(self, fields):
        # Adapt the search to the keywords that *may* be shown
        lstExclude=[]
        qAlternative = None
        oErr = ErrHandle()

        try:
            istatuslist = fields.get("istatuslist")
            if istatuslist is None or len(istatuslist) == 0:
                # Make sure only the 'show' ones are actually shown
                lstExclude.append(Q(installation_status__name="hide"))

        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationList/adapt_search")
        
        return fields, lstExclude, qAlternative


class InstallationListMap(InstallationList):
    """Derived from Installation list, but now starting with the map view"""

    start_with_list = False


class InstallationMap(MapView):
    """Mapview that leans on the InstallationList listview"""

    model = Installation    # This is the basic model of the related listview
    modEntry = Installation # Each point on the map is defined by a Location object
    use_object = False      # We are **not** grouping around one language
    prefix = "map"          # Needs to differ from the ``InstallationList`` prefix
    use_object = False      # Possible item to focus on
    use_lv = True           # Making use of listview
    param_list = ""
    frmSearch = InstallationSearchForm

    def initialize(self):
        super(InstallationMap, self).initialize()

        oErr = ErrHandle()
        try:
            # Entries with a 'form' value
            self.entry_list = []

            # Get the location's details: name, id, x-coordinate, y-coordinate
            self.add_entry('locname',       'str', 'english_name')
            # OLD: just the location = self.add_entry('location_id',   'str', 'location__id')
            self.add_entry('location_id',   'str', 'id')
            # labels 'point_x' and 'point_y' must be used for the coordinates
            self.add_entry('point_x',       'str', 'location__x_coordinate')
            self.add_entry('point_y',       'str', 'location__y_coordinate')
            # The key grouping elements for this location
            self.add_entry('trefwoord',     'str', 'installation_type__name')
            self.add_entry('info',          'str', 'english_name')


            if self.use_lv:
                # Get a version of the current listview
                lv = InstallationList()
                lv.initializations()
                # Get the list of [Installation] elements
                qs_installation = lv.get_queryset(self.request)
                # Figure out what the list of installations will be
                lst_installation = qs_installation.values('id')

                # Get all the installations selected (or is this the same as qs_installation?)
                qs_loc = Installation.objects.filter(id__in=lst_installation)
            else:
                # Take the whole
                qs_loc = Installation.objects.all()


            # Essential: make sure that self.qs gets filled
            self.qs = qs_loc

        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationMap/initialize")
        return None

    def add_geojson(self, lst_this):
        """Possibly add to the list with geojson items"""

        oErr = ErrHandle()
        exclude_fields = ['point', 'point_x', 'point_y', 'pop_up', 'locatie', 'country', 'city']
        try:
            # Walk the Installation qs
            for installation in self.qs:
                # Get all the geojson images connected with this one
                for geo in installation.images.filter(geojson__isnull=False):
                    # Get the JSON for this image
                    geojson = geo.geojson
                    info = ""
                    if not geojson is None:
                        # Get the name
                        info = geojson.get("name")
                        # Get the first point
                        bHavePoint = False
                        for oFt in geojson['features']:
                            geometry = oFt.get("geometry")
                            if not geometry is None:
                                coordinates = geometry.get("coordinates")
                                if not coordinates is None and len(coordinates) > 0:
                                    # Get the point
                                    point = coordinates[0]
                                    # Make sure it is an actual point!
                                    if isinstance(point[0], list):
                                        point = point[0]
                                        if isinstance(point[0], list):
                                            point = point[0]
                                    # Divide the point into (x,y): contrary to expectations (1,0)
                                    point_x = point[1]
                                    point_y = point[0]
                                    bHavePoint = True
                            break
                    if bHavePoint:
                        sTrefwoord = installation.get_value("instaltype")
                        if sTrefwoord is None or sTrefwoord == "":
                            # Worst case scenario
                            sTrefwoord = "geojson"
                        # Add an entry to lst_this
                        oEntry = dict(
                            locname=installation.english_name,
                            point_x = point_x,
                            point_y = point_y,
                            point = "{}, {}".format(point_x, point_y),
                            pop_up = "(no popup specified)",
                            trefwoord = sTrefwoord,
                            location_id = installation.id,
                            info = info,
                            geojson = geojson
                            )
                        lst_this.append(oEntry)

        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationMap/add_geojson")

        return lst_this

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
                        info=oEntry['info'],
                        geojson=oEntry.get('geojson')
                        )
                # Possibly add focus
                if oEntry.get("focus"):
                    set_point[point]['focus'] = True

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
            if not oPoint['locid'] is None:
                # Figure out what the link would be to this list of items
                # OLD: location. url = reverse('location_details', kwargs={'pk': oPoint['locid']})
                url = reverse('installation_details', kwargs={'pk': oPoint['locid']})
                # Create the popup
                long_title = oPoint['locatie']
                short_title = oPoint['locatie'][:30]
                if len(short_title) < len(long_title):
                    short_title += "..."
                pop_up = '<p class="h4" title="{}">{}</p>'.format(long_title, short_title)
                pop_up += '<hr style="border: 1px solid green" />'
                popup_title_1 = _("Show")
                popup_title_2 = _("objects in the list")
                # sLanguage = "exists" if oPoint['trefwoord'] == "True" else "extinct"
                sLanguage = oPoint['info']
                pop_up += '<p style="font-size: large;"><a href="{}" title="{} {} {}"><span style="color: purple;">{}</span> installation ({})</a></p>'.format(
                    url, popup_title_1, oPoint['count'],popup_title_2, oPoint['count'], oPoint['trefwoord'])
        except:
            msg = oErr.get_error_message()
            oErr.DoError("InstallationMap/get_group_popup")
        return pop_up

    def add_to_data(self, data):
        # Add edit permission to data
        data = get_application_context(self.request, data)
        # Return what we have
        return data


class InstallationFocusMap(InstallationMap):
    """Mapview that shows complete inventory, while also focusing one one item"""

    use_lv = False
    use_object = True   # Possible item to focus on


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
                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()},
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

                {'type': 'plain', 'label': 'description',       'value': instance.get_description_md()   },
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

    def check_hlist(self, instance):
        """Check if a hlist parameter is given, and hlist saving is called for"""

        oErr = ErrHandle()
        bChanges = False
        bDebug = True

        try:
            arg_hlist = "evnt-hlist"
            arg_savenew = "evnt-savenew"
            if arg_hlist in self.qd and arg_savenew in self.qd:
                # Interpret the list of information that we receive
                hlist = json.loads(self.qd[arg_hlist])
                # Interpret the savenew parameter
                savenew = self.qd[arg_savenew]

                # Make sure we are not saving
                self.do_not_save = True
                # But that we do a new redirect
                self.newRedirect = True

                # Change the redirect URL
                if self.redirectpage == "":
                    self.redirectpage = reverse('literature_details', kwargs={'pk': instance.id})

                # See if any need to be removed
                existing_item_id = [str(x.id) for x in EventLiteratureRelation.objects.filter(literature=instance)]
                delete_id = []
                for item_id in existing_item_id:
                    if not item_id in hlist:
                        delete_id.append(item_id)
                if len(delete_id)>0:
                    lstQ = [Q(literature=instance)]
                    lstQ.append(Q(**{"id__in": delete_id}))
                    EventLiteratureRelation.objects.filter(*lstQ).delete()

            return True
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Literature/check_hlist")
            return False

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'code',          'value': instance.code          },
                {'type': 'plain', 'label': 'title',         'value': instance.title         },
                {'type': 'plain', 'label': 'author',        'value': instance.get_value("author")   },
                {'type': 'plain', 'label': 'editor',        'value': instance.get_value("editor")   },
                {'type': 'plain', 'label': 'publisher',     'value': instance.get_value("publisher")},
                {'type': 'plain', 'label': 'place',         'value': instance.get_value("place")    },
                {'type': 'plain', 'label': 'year',          'value': instance.get_value("year")     },
                {'type': 'plain', 'label': 'journal',       'value': instance.get_value("journal")  },
                {'type': 'plain', 'label': 'volume',        'value': instance.get_value("volume")   },
                {'type': 'plain', 'label': 'issue',         'value': instance.get_value("issue")    },
                {'type': 'plain', 'label': 'pages',         'value': instance.get_value("pages")    },

                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()   },
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

    def custom_init(self, instance):
        # First get the 'standard' context from TestsetEdit
        super(LiteratureDetails, self).custom_init(instance)

        if not instance is None:
            self.check_hlist(instance)
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        # First get the 'standard' context from TestsetEdit
        context = super(LiteratureDetails, self).add_to_context(context, instance)

        oErr = ErrHandle()
        try:
            bMayEdit = context['is_app_editor']
                
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

            # events['editable'] = bMayEdit
            events['savebuttons'] = bMayEdit
            events['saveasbutton'] = True

            rel_list = []
            qs = EventLiteratureRelation.objects.filter(literature=instance).exclude(
                    event__isnull=True, text_type__isnull=True).order_by(
                    'event__start_date', 'event__end_date', 'event__name')
            for item in qs:
                event = item.event
                url = None
                if not event is None: 
                    url = reverse("event_details", kwargs={'pk': event.id})
                # url_relation = reverse("eventliteraturerelation_details", kwargs={'pk': item.id})
                url_relation = None
                rel_item = []
                
                # Order number for this item
                add_rel_item(rel_item, index, False, align="right")
                index += 1

                # Texttype of relation
                add_rel_item(rel_item, item.get_value('texttype'), False, main=False, nowrap=True, link=url_relation)

                # Name of event
                add_rel_item(rel_item, item.get_value('eventname'), False, main=True, nowrap=False, link=url)

                # start date
                add_rel_item(rel_item, item.get_value('startdate'), False, main=False, nowrap=True, link=url)

                # end date
                add_rel_item(rel_item, item.get_value('enddate'), False, main=False, nowrap=True, link=url)

                # Literature page range
                add_rel_item(rel_item, item.get_value('pages'), False, main=False, nowrap=True, link=url_relation)

                # Actions that can be performed on this item
                if bMayEdit:
                    add_rel_item(rel_item, self.get_actions())

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
            if bMayEdit:
                events['columns'].append("")
            related_objects.append(events)

            # Add all related objects to the context
            context['related_objects'] = related_objects
        except:
            msg = oErr.get_error_message()
            oErr.DoError("LiteratureDetails/add_to_context")

        # Return the context we have made
        return context

    def get_actions(self):
        html = []
        buttons = ['remove']    # This contains all the button names that need to be added

        # Start the whole div
        html.append("<div class='blinded'>")
        
        # Add components
        if 'remove' in buttons: 
            html.append("<a class='related-remove'><span class='glyphicon glyphicon-remove fa fa-remove'></span></a>")

        # Finish up the div
        html.append("&nbsp;</div>")

        # COmbine the list into a string
        sHtml = "\n".join(html)
        # Return out HTML string
        return sHtml


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
                {'type': 'plain', 'label': 'type',          'value': instance.get_value('type')     },

                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()  },
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


# --------------------- Person Symbol ------------------------------------

class PersonSymbolEdit(BasicDetails):
    """Simple view mode of [PersonSymbol]"""

    model = PersonSymbol
    mForm = PersonSymbolForm
    prefix = "psymb"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        #self.listview = reverse('utilities:list_view', kwargs={
        #    'model_name': 'PersonSymbol', 'app_name': 'installations'})
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()
        field_keys = [None, None, 'description', 'comments']
        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'name',          'value': instance.get_value("name")},
                {'type': 'plain', 'label': 'icon',          'value': instance.get_value("icon")},

                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()},
                {'type': 'plain', 'label': 'comments',      'value': instance.comments},
            ]
            context['title'] = "View person symbol"
            context['editview'] = reverse("installations:edit_personsymbol", kwargs={'pk': instance.id})

            may_edit = context['is_app_moderator'] or context['is_app_developer']
            # Only moderators and superusers are to be allowed to create and delete content-items
            if may_edit: 
                # Allow editing
                for idx, oItem in enumerate(context['mainitems']):
                    fk = field_keys[idx]
                    if not fk is None:
                        oItem['field_key'] = fk

                # Only the superuser may edit the name
                if context["is_app_developer"]:
                    context['mainitems'][0]['field_key'] = "name"

                # Signal that we have select2
                context['has_select2'] = True
            else:
                # Make sure user cannot delete
                self.no_delete = True

        except:
            msg = oErr.get_error_message()
            oErr.DoError("PersonSymbolDetails/add_to_context")

        # Return the context we have made
        return context


class PersonSymbolDetails(PersonSymbolEdit):
    rtype = "html"


class PersonSymbolList(BasicList):
    """List and search view for PersonSymbol"""

    model = PersonSymbol 
    listform = PersonSymbolSearchForm
    prefix = "symb"
    has_select2 = True
    sg_name = "Person Symbol"       # This is the name as it appears e.g. in "Add a new XXX" (in the basic listview)
    plural_name = "Person Symbols"  # As displayed
    new_button = False              # Normally this is false, unless this is someone with editing rights
    fontawesome_already = True      # Already have fontawesome
    order_cols = ['name', '', '']
    order_default = order_cols
    order_heads = [
        {'name': 'Name',        'order': 'o=1', 'type': 'str', 'custom': 'name',        'linkdetails': True,  'main': True},
        {'name': 'Icon',        'order': '',    'type': 'str', 'custom': 'icon',        'linkdetails': True               },
        {'name': 'Description', 'order': '',    'type': 'str', 'custom': 'description', 'linkdetails': True               },
        ]
                   
    filters = [ 
        {"name": "Name",            "id": "filter_name",        "enabled": False},
        {"name": "Description",     "id": "filter_description", "enabled": False},
        ]
    searches = [
        {'section': '', 'filterlist': [
            {'filter': 'name',          'dbfield': 'name',          'keyS': 'name'},
            {'filter': 'description',   'dbfield': 'description',   'keyS': 'description'},
            ]
         } 
        ] 

    def add_to_context(self, context, initial):
        # may_add = context['is_app_moderator'] or context['is_app_developer']
        # Note: only the S.U. may actually add one
        may_add = context['is_app_developer']
        if may_add:
            # Allow creation of new item(s)
            self.new_button = True
            context['new_button'] = self.new_button
            self.basic_add = reverse("installations:add_personsymbol")
            context['basic_add'] = self.basic_add
        return context

    def get_field_value(self, instance, custom):
        """Define what is actually displayed"""

        sBack = ""
        sTitle = ""
        html = []
        oErr = ErrHandle()
        try:
            if custom == "name":
                # Get the correctly visible date
                sBack = instance.get_value("name")

            if custom == "icon":
                # Get the correctly visible date
                sBack = instance.get_value("icon")

            elif custom == "description":
                sBack = instance.get_description_md()
            
        except:
            msg = oErr.get_error_message()
            oErr.DoError("PersonSymbolList/get_field_value")

        return sBack, sTitle


# --------------------- Person Type ------------------------------------

class PersonTypeEdit(BasicDetails):
    """Simple view mode of [PersonType]"""

    model = PersonType
    mForm = PersonTypeForm
    prefix = "ptype"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        #self.listview = reverse('utilities:list_view', kwargs={
        #    'model_name': 'PersonType', 'app_name': 'installations'})
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'name',          'value': instance.name},
                {'type': 'plain', 'label': 'symbol',        'value': instance.get_value('symbol')},

                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()},
                {'type': 'plain', 'label': 'comments',      'value': instance.comments},
            ]
            context['title'] = "View person type"
            context['editview'] = reverse("installations:edit_persontype", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("PersonTypeDetails/add_to_context")

        # Return the context we have made
        return context


class PersonTypeDetails(PersonTypeEdit):
    rtype = "html"


class PersonTypeList(BasicList):
    """List and search view for PersonType"""

    model = PersonType 
    listform = PersonTypeSearchForm
    prefix = "symb"
    has_select2 = True
    sg_name = "Person Type"       # This is the name as it appears e.g. in "Add a new XXX" (in the basic listview)
    plural_name = "Person Types"  # As displayed
    new_button = False              # Normally this is false, unless this is someone with editing rights
    fontawesome_already = True      # Already have fontawesome
    order_cols = ['name', 'symbol__name', '']
    order_default = order_cols
    order_heads = [
        {'name': 'Name',        'order': 'o=1', 'type': 'str', 'custom': 'name',        'linkdetails': True,  'main': True},
        {'name': 'Symbol',      'order': '',    'type': 'str', 'custom': 'symbol',      'linkdetails': True               },
        {'name': 'Description', 'order': '',    'type': 'str', 'custom': 'description', 'linkdetails': True               },
        ]
                   
    filters = [ 
        {"name": "Name",            "id": "filter_name",        "enabled": False},
        {"name": "Symbol",          "id": "filter_symbol",      "enabled": False},
        {"name": "Description",     "id": "filter_description", "enabled": False},
        ]
    searches = [
        {'section': '', 'filterlist': [
            {'filter': 'name',          'dbfield': 'name',          'keyS': 'name'},
            {'filter': 'symbol',         'fkfield': 'symbol',        'keyFk': 'name', 
             'keyList': 'symbollist',    'infield': 'name'},
            {'filter': 'description',   'dbfield': 'description',   'keyS': 'description'},
            ]
         } 
        ] 

    def add_to_context(self, context, initial):
        may_add = context['is_app_moderator'] or context['is_app_developer']
        if may_add:
            # Allow creation of new item(s)
            self.new_button = True
            context['new_button'] = self.new_button
            self.basic_add = reverse("installations:add_persontype")
            context['basic_add'] = self.basic_add
        return context

    def get_field_value(self, instance, custom):
        """Define what is actually displayed"""

        sBack = ""
        sTitle = ""
        html = []
        oErr = ErrHandle()
        try:
            if custom == "name":
                # Get the correctly visible date
                sBack = instance.get_value("name")

            elif custom == "symbol":
                # Get the correctly visible date
                sBack = instance.get_value("symbol")

            elif custom == "description":
                sBack = instance.get_description_md()
            
        except:
            msg = oErr.get_error_message()
            oErr.DoError("PersonTypeList/get_field_value")

        return sBack, sTitle


# --------------------- Location ----------------------------------------------

class LocationEdit(BasicDetails):
    """Simple view mode of [Location]"""

    model = Location
    mForm = LocationForm
    prefix = "loc"
    mainitems = []

    def custom_init(self, instance, **kwargs):
        self.listview = reverse('utilities:list_view', kwargs={'model_name': 'Location', 'app_name': 'installations' })
        return None

    def add_to_context(self, context, instance):
        """Add to the existing context"""

        oErr = ErrHandle()

        try:
            context['mainitems'] = [
                {'type': 'plain', 'label': 'name',          'value': instance.name          },
                {'type': 'plain', 'label': 'type',          'value': instance.get_loctype() },
                {'type': 'plain', 'label': 'longitude',     'value': instance.x_coordinate  },
                {'type': 'plain', 'label': 'latitude',      'value': instance.y_coordinate  },
            ]
            context['title'] = "View Location"
            context['editview'] = reverse("installations:edit_location", kwargs={'pk': instance.id})
        except:
            msg = oErr.get_error_message()
            oErr.DoError("LocationDetails/add_to_context")

        # Return the context we have made
        return context

    def before_save(self, form, instance):
        """Before saving a new Location"""

        bResult = True
        msg = ""
        oErr = ErrHandle()
        try:
            # Try to retrieve the marker location
            marker_loc = self.qd.get("marker_loc")
            if not marker_loc is None and marker_loc != "":
                # This is a stringified json
                oGeoJson = json.loads(marker_loc)
                # Find the actual location
                coords = oGeoJson.get("geometry").get("coordinates")
                form.instance.x_coordinate = str(coords[1])
                form.instance.y_coordinate = str(coords[0])
                form.instance.loctype = LocType.get_item("mappoint")
        except:
            msg = oErr.get_error_message()
            oErr.DoError("LocationEdit/before_save")
        return bResult, msg


class LocationDetails(LocationEdit):
    rtype = "html"


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
                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()},
                {'type': 'plain', 'label': 'comments',      'value': instance.comments},
            ]
            context['title'] = "View Purpose"
            context['editview'] = reverse("installations:edit_purpose", kwargs={'pk': instance.id})
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
                add_rel_item(rel_item, installation.get_value('systems'), False, main=False, nowrap=True) #, link=url)

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
                {'type': 'plain', 'label': 'location',      'value': instance.get_value('location')     },
                {'type': 'plain', 'label': 'description',   'value': instance.get_description_md()  },
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


