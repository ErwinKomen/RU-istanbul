from django.db import models
from partial_date import PartialDateField
from colorfield.fields import ColorField
from utils.model_util import info


dargs = {'on_delete':models.SET_NULL,'blank':True,'null':True}

class Religion(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True, unique=True)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

class System(models.Model, info):
    original_name = models.CharField(max_length=1000,blank=True,null=True)
    ottoman_name = models.CharField(max_length=1000,blank=True,null=True)
    english_name = models.CharField(max_length=1000,blank=True,null=True,
        unique=True)
    turkish_name = models.CharField(max_length=1000,blank=True,null=True)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

class Gender(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)

class Person(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)
    gender = models.ForeignKey(Gender,**dargs)
    birth_year = PartialDateField(null=True,blank=True)
    death_year = PartialDateField(null=True,blank=True)
    start_reign = PartialDateField(null=True,blank=True)
    end_reign = PartialDateField(null=True,blank=True)
    religion = models.ForeignKey(Religion,**dargs)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

    class Meta:
        unique_together = [['name','birth_year','death_year']]

class InstitutionType(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

class Institution(models.Model, info):
    original_name = models.CharField(max_length=1000,blank=True,null=True)
    ottoman_name = models.CharField(max_length=1000,blank=True,null=True)
    english_name = models.CharField(max_length=1000,blank=True,null=True,
        unique = True)
    turkish_name = models.CharField(max_length=1000,blank=True,null=True)
    institution_type = models.ForeignKey(InstitutionType,**dargs)
    religion = models.ForeignKey(Religion,**dargs)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

class EventType(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

class Image(models.Model, info):
    gpsargs = {'blank':True,'null':True,'max_digits':8,'decimal_places':5}
    image_file = models.FileField(upload_to='IMAGES/',null=True,blank=True)
    maker = models.CharField(max_length=300,blank=True,null=True)
    year = PartialDateField(null=True,blank=True)
    title = models.CharField(max_length=300,blank=True,null=True)
    url= models.CharField(max_length=1000,blank=True,null=True)
    current_location= models.CharField(max_length=300,blank=True,null=True)
    collection = models.CharField(max_length=300,blank=True,null=True)
    description = models.TextField(default = '')
    latitude = models.DecimalField(**gpsargs)
    longitude = models.DecimalField(**gpsargs)
    comments = models.TextField(default = '')

class Style(models.Model, info):
    name = models.CharField(max_length=300)
    color = ColorField(default='#FF0000')
    line_thickness = models.IntegerField(default = 2,blank=True,null=True)
    fill_opacity = models.FloatField(default = 0.3, blank=True,null=True)
    line_opacity = models.FloatField(default = 0.3, blank=True,null=True)
    dashed = models.BooleanField(default =False) 
    z_index = models.IntegerField(default = 0, blank=True,null=True)
    
class Figure(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)
    geojson= models.FileField(upload_to='GEOJSON/',null=True,blank=True)
    style = models.ForeignKey(Style,**dargs)

class Event(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)
    event_type = models.ForeignKey(EventType,**dargs)
    start_date = PartialDateField(null=True,blank=True)
    end_date = PartialDateField(null=True,blank=True)
    date_comments = models.TextField(default = '')
    images = models.ManyToManyField(Image,blank=True,default= None)
    figure = models.ForeignKey(Figure,**dargs)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

    class Meta:
        unique_together = [['name','start_date','end_date']]

    @property
    def personrelations(self):
        return self.eventpersonrelation_set.all()

class Purpose(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')

class InstallationType(models.Model, info):
    name = models.CharField(max_length=300,blank=True,null=True)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')
    

class Installation(models.Model, info):
    original_name = models.CharField(max_length=1000,blank=True,null=True)
    ottoman_name = models.CharField(max_length=1000,blank=True,null=True)
    english_name = models.CharField(max_length=1000,blank=True,null=True,
        unique=True)
    turkish_name = models.CharField(max_length=1000,blank=True,null=True)
    installation_type = models.ForeignKey(InstallationType,**dargs)
    events = models.ManyToManyField(Event,blank=True,default= None)
    purposes = models.ManyToManyField(Purpose,blank=True,default= None)
    images = models.ManyToManyField(Image,blank=True,default= None)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')
    still_exists = models.BooleanField(blank=True,null=True)

    @property
    def detail_url(self):
        return 'installations:detail_installation_view'

class Literature(models.Model, info):
    code = models.CharField(max_length=300,blank=True,null=True, unique = True)
    title= models.CharField(max_length=300,blank=True,null=True)
    author= models.CharField(max_length=300,blank=True,null=True)
    editor= models.CharField(max_length=300,blank=True,null=True)
    publisher= models.CharField(max_length=300,blank=True,null=True)
    place= models.CharField(max_length=300,blank=True,null=True)
    year= models.CharField(max_length=100,blank=True,null=True)
    journal= models.CharField(max_length=300,blank=True,null=True)
    volume= models.CharField(max_length=100,blank=True,null=True)
    page_numbers= models.CharField(max_length=100,blank=True,null=True)
    issue= models.CharField(max_length=100,blank=True,null=True)
    text = models.TextField(default = '')
    comments = models.TextField(default = '')
    description = models.TextField(default = '')
    
class SystemInstallationRelation(models.Model, info):
    system = models.ForeignKey(System,**dargs)
    installation = models.ForeignKey(Installation,**dargs)
    start_date = PartialDateField(null=True,blank=True)
    end_date = PartialDateField(null=True,blank=True)
    description = models.TextField(default = '')
    comments = models.TextField(default = '')
    is_part_of = models.BooleanField(blank=True,null=True)

class TextType(models.Model, info):
    name = models.CharField(max_length=100,blank=True,null=True)

class EventRole(models.Model, info):
    name = models.CharField(max_length=100,blank=True,null=True)

class EventLiteratureRelation(models.Model, info):
    event = models.ForeignKey(Event,**dargs)
    literature = models.ForeignKey(Literature,**dargs)
    page_number= models.CharField(max_length=100,blank=True,null=True)
    text = models.TextField(default = '')
    text_file = models.FileField(upload_to='FILES/',null=True,blank=True)
    text_type = models.ForeignKey(TextType,**dargs)

class EventInstitutionRelation(models.Model, info):
    event = models.ForeignKey(Event, **dargs)
    institution= models.ForeignKey(Institution, **dargs)
    role = models.ForeignKey(EventRole, **dargs)
    
class EventPersonRelation(models.Model, info):
    event = models.ForeignKey(Event, **dargs)
    person= models.ForeignKey(Person, **dargs)
    role = models.ForeignKey(EventRole, **dargs)

    @property
    def person_role(self):
        return self.person.name + ' ' + self.role.name
    

