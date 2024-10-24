"""
Main models for the istanbul-su application
"""
import os
from re import X
from django.db import models
from django.urls import reverse
from partial_date import PartialDateField
from colorfield.fields import ColorField

# idiosyncratics
from partial_date import PartialDate

# From own application
from basic.utils import ErrHandle
from utils.model_util import info


# Default arguments for *OPTIONAL* ForeignKey
dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}

# ========================== Main classes ===================================

class Religion(models.Model, info):
    """One of the religions related to the Water entities"""

    # [0-1] Name of the religion
    name = models.CharField(max_length=300,blank=True,null=True, unique=True)
    # [1] Description of the religion
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user)
    comments = models.TextField(default = '')


class System(models.Model, info):
    """A water system, such as a 'waterway' - a channel"""

    # [0-1] Name of the system in the original language
    original_name = models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Name of the system in the Ottoman language
    ottoman_name = models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Name of the system in the English language
    english_name = models.CharField(max_length=1000,blank=True,null=True,
        unique=True)
    # [0-1] Name of the system in the Turkish language
    turkish_name = models.CharField(max_length=1000,blank=True,null=True)
    # [1] Description of the system (can be just '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')


class Gender(models.Model, info):
    """Names of genders that are defined"""

    # [0-1] Name of the gender
    name = models.CharField(max_length=300,blank=True,null=True)


class Person(models.Model, info):
    """Person of historical interest, including e.g. rulers"""

    # [0-1] Name of the person (in English)
    name = models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Gender of the person (male/female)
    gender = models.ForeignKey(Gender,**dargs)
    # [0-1] Year in which the person was born
    birth_year = PartialDateField(null=True,blank=True)
    # [0-1] Year in which the person was died
    death_year = PartialDateField(null=True,blank=True)
    # [0-1] Year in which the person started to reign
    start_reign = PartialDateField(null=True,blank=True)
    # [0-1] Year in which the person ended reigning
    end_reign = PartialDateField(null=True,blank=True)
    # [0-1] Religion of this person
    religion = models.ForeignKey(Religion,**dargs)
    # [1] Description of the person (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')

    class Meta:
        unique_together = [['name','birth_year','death_year']]

    def get_value(self, field):
        """Get the value(s) of 'field' associated with this installation"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:

            if field == "gender":
                if not self.gender is None:
                    sBack = self.gender.name
            elif field == "religion":
                if not self.religion is None:
                    sBack = self.religion.name
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Person/get_value")

        return sBack


class InstitutionType(models.Model, info):
    """An institution type"""

    # [0-1] The name of the institution type
    name = models.CharField(max_length=300,blank=True,null=True)

    # =========== Standard fields ========================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')


class Institution(models.Model, info):
    """An institution type"""

    # [0-1] Name of the system in the original language
    original_name = models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Name of the system in the original language
    ottoman_name = models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Name of the system in the original language
    english_name = models.CharField(max_length=1000,blank=True,null=True,
        unique = True)
    # [0-1] Name of the system in the original language
    turkish_name = models.CharField(max_length=1000,blank=True,null=True)

    # ==================== Links to other objects ========================
    # [0-1] Type of institution
    institution_type = models.ForeignKey(InstitutionType,**dargs)
    # [0-1] Religion
    religion = models.ForeignKey(Religion,**dargs)

    # =========== Standard fields ========================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')

    def get_value(self, field):
        """Get the value(s) of 'field' associated with this institution"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:

            if field == "instittype":
                if not self.institution_type is None:
                    sBack = self.institution_type.name
            elif field == "religion":
                if not self.religion is None:
                    sBack = self.religion.name
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Institution/get_value")

        return sBack


class EventType(models.Model, info):
    """An event type"""

    # [0-1] The name of the event type
    name = models.CharField(max_length=300,blank=True,null=True)

    # =========== Standard fields ========================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')


class Image(models.Model, info):
    """An image related to an event"""

    # Class settings [gpsargs]
    gpsargs = {'blank':True,'null':True,'max_digits':8,'decimal_places':5}

    # [1] The actual image
    image_file = models.FileField(upload_to='IMAGES/',null=True,blank=True)
    # [0-1] Name of the maker(s) of this image
    maker = models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Year when this image was published
    year = PartialDateField(null=True,blank=True)
    # [0-1] Title of the image
    title = models.CharField(max_length=300,blank=True,null=True)
    # [0-1] URL to the location of this image
    url= models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Where this image is currently kept
    current_location= models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Name of the collection this belongs to
    collection = models.CharField(max_length=300,blank=True,null=True)
    # [1] Image location latitude coordinate
    latitude = models.DecimalField(**gpsargs)
    # [1] Image location longitude coordinate
    longitude = models.DecimalField(**gpsargs)

    # =========== Standard fields ========================================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')

    def get_image_html(self, tooltip=None):
        """Get the HTML <img> code for this one"""

        oErr = ErrHandle()
        sBack = ""
        sTitle = ""

        try:
            # Get the number of the image, depending on the options
            image = self.image_file.url
            sTitle = self.title
            descr = self.description
            sClass = "stalla-image" # Was: col-md-12

            if ".geojson" in image.lower():
                # This is a geojson file that I cannot show
                sBack = "<span title='{}'>geojson file</span>".format(image)
            else:

                if tooltip == None:
                    sBack = "<img src='{}' alt='{}' class='{}' >".format(image, descr, sClass)
                else:
                    sBack = "<img src='{}' alt='{}' data-toggle='tooltip' data-tooltip='werkstuk-hover' title='{}' class='{}'>".format(
                        image, descr, tooltip, sClass)

        except:
            msg = oErr.get_error_message()
            oErr.DoError("Image/get_image_html")
        return sBack, sTitle

    def get_label(self):
        """Get a representative label for this image"""

        if self.title:
            sBack = self.title
        else:
            sBack = "image_{}".format(self.id)
        return sBack

    def get_value(self, field):
        """Get the value(s) of 'field' associated with this image"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:
            if field == "coordinate":
                if not self.latitude is None and not self.longitude is None:
                    sBack = "{} {}".format(self.latitude, self.longitude)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Event/get_value")

        return sBack


class Style(models.Model, info):
    """Style of a particular figure"""

    # [1] Name of the style
    name = models.CharField(max_length=300)
    # [1] Color used in this style
    color = ColorField(default='#FF0000')
    # [0-1] Line thickness for this style
    line_thickness = models.IntegerField(default = 2,blank=True,null=True)
    # [0-1] Fill opacity for this style
    fill_opacity = models.FloatField(default = 0.3, blank=True,null=True)
    # [0-1] Line opacity for this style
    line_opacity = models.FloatField(default = 0.3, blank=True,null=True)
    # [1] Whether lines are dashed or not
    dashed = models.BooleanField(default =False) 
    # [0-1] How far to the front or back this figure is
    z_index = models.IntegerField(default = 0, blank=True,null=True)
 
    
class Figure(models.Model, info):
    """Figure related to an event"""

    # [0-1] Name of the figure
    name = models.CharField(max_length=300,blank=True,null=True)
    # [0-1] File containing geojson data related to the figure
    geojson= models.FileField(upload_to='GEOJSON/',null=True,blank=True)

    # ==================== Links to other objects ========================
    # [0-1] Style of the figure
    style = models.ForeignKey(Style,**dargs)


class Event(models.Model, info):
    """Construction, addition or other event related to a water work"""

    # [0-1] Name of the event
    name = models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Year when event started
    start_date = PartialDateField(null=True,blank=True)
    # [0-1] Year when event finished
    end_date = PartialDateField(null=True,blank=True)
    # [1] Comments on the dating (may be '')
    date_comments = models.TextField(default = '')

    # ==================== Links to other objects ========================
    # [0-1] Type of event (construction, addition etc)
    event_type = models.ForeignKey(EventType,**dargs)
    # [0-1] Figure related to this event
    figure = models.ForeignKey(Figure,**dargs)

    # ==================== Many-to-many fields ===========================
    # [0-1] Images related to this event
    images = models.ManyToManyField(Image,blank=True,default= None)

    # =========== Standard fields ========================================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')

    class Meta:
        unique_together = [['name','start_date','end_date']]

    @property
    def personrelations(self):
        # OLD: qs = self.eventpersonrelation_set.all()
        qs = self.eventpersonrelations.all()
        return qs

    def label(oItem, options = {}):
        """Construct a label from the three strings"""

        sBack = ""
        oErr = ErrHandle()
        start_date = None
        end_date = None
        try:
            skipname = options.get("skipname")
            if skipname:
                # Try to filter it out
                name = oItem.get('name')
                name = name.replace("{} - ".format(skipname), "")
                name = name.replace(skipname, "")
            else:
                name = oItem.get('name')
            if oItem.get('start_date'):
                start_date = oItem.get('start_date').year
            if oItem.get('end_date'):
                end_date = oItem.get('end_date').year
            sBack = name
            if start_date: 
                sBack += ' ' + str(start_date)
            if start_date and end_date: 
                sBack += ' -'
            if end_date: 
                sBack += ' ' + str(end_date)
            # Possible modification
            sBack = sBack.strip()
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Event/label")

        return sBack

    def get_value(self, field, options = {}):
        """Get the value(s) of 'field' associated with this installation"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:
            if field == "startdate":
                if not self.start_date is None:
                    sBack = self.start_date.year
            elif field == "enddate":
                if not self.end_date is None:
                    sBack = self.end_date.year
            elif field == "eventtype":
                if not self.event_type is None:
                    sBack = self.event_type.name
            elif field == "installations":
                # Sort the installations by their English name, if possible
                for oItem in self.installation_set.all().values('id', 'english_name').order_by('english_name'):
                    url = reverse('installation_details', kwargs={'pk': oItem['id']})
                    label = Installation.label(oItem)
                    sItem = "<span class='badge signature gr'><a class='nostyle' href='{}'>{}</a></span>".format(url, label)
                    sItem = "<div>{}</div>".format(sItem)
                    lst_value.append(sItem)
                sBack = ", ".join(lst_value)
            elif field == "persons":
                # Get all persons associated with this event
                qs = Person.objects.filter(eventpersonrelations__event=self)
                for oItem in qs.values('id', 'name', 'start_reign', 'end_reign').order_by('name'):
                    url = reverse('person_details', kwargs={'pk': oItem['id']})
                    label = oItem.get('name')

                    # Get the person's role in this event
                    eventrole = EventPersonRelation.objects.filter(person_id=oItem['id'], event=self).first()
                    if not eventrole is None:
                        role = eventrole.role.name
                        label = "{} - <i>{}</i>".format(label, role)
                    
                    # Get appropriate dates
                    start_reign = oItem.get('start_reign')
                    end_reign = oItem.get('end_reign')
                    if start_reign and end_reign:
                        empire = '<i class="fa fa-empire"></i>'
                        label = "{} ({} {}-{})".format(label, empire, start_reign.year, end_reign.year)
                    sItem = '<span class="badge signature cl"><a class="nostyle" href="{}">{}</a></span>'.format(url, label)
                    lst_value.append(sItem)
                sBack = ", ".join(lst_value)
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Event/get_value")

        return sBack


class Purpose(models.Model, info):
    """A purpose (e.g. display, decoration, bathing)"""

    # [0-1] The name of the purpose
    name = models.CharField(max_length=300,blank=True,null=True)

    # =========== Standard fields ========================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')

    def __str__(self):
        sBack = ""
        if self.name:
            sBack = self.name
        else:
            sBack = self.description
        return sBack

    def get_name(self):
        sBack = ""
        if self.name:
            sBack = self.name
        return sBack


class InstallationType(models.Model, info):
    """An installation type"""

    # [0-1] The name of the installation type
    name = models.CharField(max_length=300,blank=True,null=True)

    # =========== Standard fields ========================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')

    def __str__(self):
        return self.name
    

class Installation(models.Model, info):
    """Water related installation"""

    # [0-1] Name of the system in the original language
    original_name = models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Name of the system in the Ottoman language
    ottoman_name = models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Name of the system in the English language
    english_name = models.CharField(max_length=1000,blank=True,null=True,
        unique=True)
    # [0-1] Name of the system in the Turkish language
    turkish_name = models.CharField(max_length=1000,blank=True,null=True)
    # [0-1] Whether the installation still exists
    still_exists = models.BooleanField(blank=True,null=True)

    # ==================== Links to other objects ========================
    # [0-1] Type of installation
    installation_type = models.ForeignKey(InstallationType,**dargs)

    # ==================== Many-to-many fields ===========================
    # [0-1] Images related to this installation
    events = models.ManyToManyField(Event,blank=True,default= None)
    # [0-1] Purposes related to this installation
    purposes = models.ManyToManyField(Purpose,blank=True,default= None)
    # [0-1] Images related to this installation
    images = models.ManyToManyField(Image,blank=True,default= None)

    # =========== Standard fields ========================================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')

    @property
    def detail_url(self):
        return 'installations:detail_installation_view'

    def get_value(self, field, sep=None, options={}):
        """Get the value(s) of 'field' associated with this installation"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:
            if field == "events":
                # Sort the events by DATE if possible
                for oItem in self.events.all().values('id', 'name', 'start_date', 'end_date').order_by('start_date', 'end_date', 'name'):
                    # url = reverse('installations:edit_event', kwargs={'pk': oItem['id']})
                    url = reverse('event_details', kwargs={'pk': oItem['id']})
                    label = Event.label(oItem, options)
                    sItem = "<span class='badge signature gr'><a class='nostyle' href='{}'>{}</a></span>".format(url, label)
                    # sItem = "<div>{}</div>".format(sItem)
                    lst_value.append(sItem)
                if sep:
                    sBack = sep.join(lst_value)
                else:
                    sBack = "\n".join(lst_value)
            elif field == "eventpersons":
                # Get all persons associated with installation via events
                qs = Person.objects.filter(eventpersonrelations__event__installation=self)
                for oItem in qs.values('id', 'name', 'start_reign', 'end_reign').order_by('name'):
                    url = reverse('person_details', kwargs={'pk': oItem['id']})
                    label = oItem.get('name')

                    # Get the person's roles in all events associated with this installation
                    if not options.get("skiprole", False):
                        lst_role = []
                        for event in self.events.all():
                            eventrole = EventPersonRelation.objects.filter(person_id=oItem['id'], event=event).first()
                            if not eventrole is None:
                                rolename = eventrole.role.name
                                if not rolename in lst_role:
                                    lst_role.append(rolename)
                        if len(lst_role) > 0:
                            label = "{} - <i>{}</i>".format(label, ", ".join(lst_role))

                    # If this is an emperor, get the reign dates
                    start_reign = oItem.get('start_reign')
                    end_reign = oItem.get('end_reign')
                    if start_reign and end_reign:
                        empire = '<i class="fa fa-empire"></i>'
                        label = "{} ({} {}-{})".format(label, empire, start_reign.year, end_reign.year)
                    sItem = '<span class="badge signature cl"><a class="nostyle" href="{}">{}</a></span>'.format(url, label)
                    lst_value.append(sItem)
                sBack = ", ".join(lst_value)
            elif field == "purposes":
                for oItem in self.purposes.all().values('id','name').order_by('name'):
                    # url = reverse('installations:edit_purpose', kwargs={'pk': oItem['id']})
                    url = reverse('purpose_details', kwargs={'pk': oItem['id']})
                    label = oItem.get("name")
                    sItem = '<span class="badge signature gr"><a class="nostyle" href="{}">{}</a></span>'.format(url, label)
                    lst_value.append(sItem)
                sBack = ", ".join(lst_value)
            elif field == "stillexists":
                sBack = "Yes" if self.still_exists else "No"
            elif field == "systems":
                ids = [x['system__id'] for x in SystemInstallationRelation.objects.filter(
                    installation=self, system__isnull=False).values('system__id')]
                for oItem in System.objects.filter(id__in=ids).values('id', 'english_name').order_by('english_name'):
                    # OLD: url = reverse('installations:edit_system', kwargs={'pk': oItem['id']})
                    url = reverse('system_details', kwargs={'pk': oItem['id']})
                    label = oItem.get("english_name")
                    sItem = '<span class="badge signature ot"><a class="nostyle" href="{}">{}</a></span>'.format(url, label)
                    lst_value.append(sItem)
                sBack = ", ".join(lst_value)
            elif field == "instaltype":
                if not self.installation_type is None:
                    sBack = self.installation_type.name
            elif field == "name":
                if not self.english_name is None:
                    sBack = self.english_name
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Installation/get_value")

        return sBack

    def label(oItem):
        """Construct a label from an optional number of strings"""

        sBack = ""
        oErr = ErrHandle()
        start_date = None
        end_date = None
        try:
            name = oItem.get('english_name')
            sBack = name
        except:
            msg = oErr.get_error_message()
            oErr.DoError("Installation/label")

        return sBack


class Literature(models.Model, info):
    """Literature reference as well as source text"""

    # [0-1] Author-year code
    code = models.CharField(max_length=300,blank=True,null=True, unique = True)
    # [0-1] Title of the publication or primary source
    title= models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Name of the author
    author= models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Name of the editor
    editor= models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Name of the publisher
    publisher= models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Place of publication
    place= models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Year of publication (as characters??)
    year= models.CharField(max_length=100,blank=True,null=True)
    # [0-1] Name of the journal or volume
    journal= models.CharField(max_length=300,blank=True,null=True)
    # [0-1] Volume of the journal
    volume= models.CharField(max_length=100,blank=True,null=True)
    # [0-1] Issue of the journal or volume
    page_numbers= models.CharField(max_length=100,blank=True,null=True)
    # [0-1] Issue of the journal or volume
    issue= models.CharField(max_length=100,blank=True,null=True)
    # [1] Source text
    text = models.TextField(default = '')

    # =========== Standard fields ========================================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')


# ========================== RELATIONS BETWEEN MAIN ITEMS ===============================
  
    
class SystemInstallationRelation(models.Model, info):
    """Relation between a system and an installation"""

    # [0-1] Year when link between system and installation started
    start_date = PartialDateField(null=True,blank=True)
    # [0-1] Year when link between system and installation ended
    end_date = PartialDateField(null=True,blank=True)
    # [0-1] Whether the one is part of the other
    is_part_of = models.BooleanField(blank=True,null=True)

    # ==================== Links to other objects ========================
    # [0-1] Link to system
    system = models.ForeignKey(System,**dargs)
    # [0-1] Link to Intallation
    installation = models.ForeignKey(Installation,**dargs)

    # =========== Standard fields ========================================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')


class TextType(models.Model, info):
    """Type of text"""

    # [0-1] Name of the text type
    name = models.CharField(max_length=100,blank=True,null=True)


class EventRole(models.Model, info):
    """Role of the event (e.g: builder, finisher, founder, inaugurator)"""

    # [0-1] Name of the event role
    name = models.CharField(max_length=100,blank=True,null=True)


class EventLiteratureRelation(models.Model, info):
    """Relation between a event and an literature"""

    # [0-1] Year when link between system and installation started
    page_number= models.CharField(max_length=100,blank=True,null=True)
    # The text of the text itself
    text = models.TextField(default = '')
    # The file from which the text comes
    text_file = models.FileField(upload_to='FILES/',null=True,blank=True)

    # ==================== Links to other objects ========================
    # [0-1] Link to text_type
    text_type = models.ForeignKey(TextType,**dargs)
    # [0-1] Link to event
    event = models.ForeignKey(Event,**dargs)
    # [0-1] Link to literature
    literature = models.ForeignKey(Literature,**dargs)

    def get_value(self, field):
        """Get the value(s) of 'field' associated with this event-literature relation"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:
            if field == "texttype" and self.text_type:
                sBack = self.text_type.name
            elif field == "pages" and self.page_number:
                sBack = self.page_number
            elif field == "eventname":
                if self.event is None:
                    sBack = "(No event)"
                else:
                    sBack = self.event.name
            elif field == "startdate" and not self.event is None:
                sBack = self.event.get_value("startdate")
            elif field == "enddate" and not self.event is None:
                sBack = self.event.get_value("enddate")

        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventLiteratureRelation/get_value")

        return sBack


class EventInstitutionRelation(models.Model, info):
    """Relation between an event and an institution"""

    # ==================== Links to other objects ========================
    # [0-1] Link to event
    event = models.ForeignKey(Event, **dargs)
    # [0-1] Link to institution
    institution= models.ForeignKey(Institution, **dargs)
    # [0-1] Link to event role
    role = models.ForeignKey(EventRole, **dargs)

    def get_value(self, field):
        """Get the value(s) of 'field' associated with this event-institution relation"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:
            if field == "role" and self.role:
                sBack = self.role.name

        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventInstitutionRelation/get_value")

        return sBack


class EventPersonRelation(models.Model, info):
    """Relation between an event and a person"""

    # ==================== Links to other objects ========================
    # [0-1] Link to event
    event = models.ForeignKey(Event, **dargs, related_name="eventpersonrelations")
    # [0-1] Link to person
    person= models.ForeignKey(Person, **dargs, related_name="eventpersonrelations")
    # [0-1] Link to event role
    role = models.ForeignKey(EventRole, **dargs, related_name="eventpersonrelations")

    @property
    def person_role(self):
        return self.person.name + ' ' + self.role.name
    
    def get_value(self, field):
        """Get the value(s) of 'field' associated with this event-person relation"""

        sBack = ""
        lst_value = []
        oErr = ErrHandle()
        try:
            if field == "role" and self.role:
                sBack = self.role.name

        except:
            msg = oErr.get_error_message()
            oErr.DoError("EventPersonRelation/get_value")

        return sBack


