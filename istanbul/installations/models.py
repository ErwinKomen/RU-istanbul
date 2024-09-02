"""
Main models for the istanbul-su application
"""
from django.db import models
from partial_date import PartialDateField
from colorfield.fields import ColorField

# From own application
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
        return self.eventpersonrelation_set.all()


class Purpose(models.Model, info):
    """A purpose (e.g. display, decoration, bathing)"""

    # [0-1] The name of the purpose
    name = models.CharField(max_length=300,blank=True,null=True)

    # =========== Standard fields ========================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')


class InstallationType(models.Model, info):
    """An installation type"""

    # [0-1] The name of the installation type
    name = models.CharField(max_length=300,blank=True,null=True)

    # =========== Standard fields ========================
    # [1] Description of this object (may be '')
    description = models.TextField(default = '')
    # [1] Additional info (not visible for end user - can be just '')
    comments = models.TextField(default = '')
    

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


class EventInstitutionRelation(models.Model, info):
    """Relation between an event and an institution"""

    # ==================== Links to other objects ========================
    # [0-1] Link to event
    event = models.ForeignKey(Event, **dargs)
    # [0-1] Link to institution
    institution= models.ForeignKey(Institution, **dargs)
    # [0-1] Link to event role
    role = models.ForeignKey(EventRole, **dargs)
    

class EventPersonRelation(models.Model, info):
    """Relation between an event and a person"""

    # ==================== Links to other objects ========================
    # [0-1] Link to event
    event = models.ForeignKey(Event, **dargs)
    # [0-1] Link to person
    person= models.ForeignKey(Person, **dargs)
    # [0-1] Link to event role
    role = models.ForeignKey(EventRole, **dargs)

    @property
    def person_role(self):
        return self.person.name + ' ' + self.role.name
    

