from .models import System, Religion, Gender, Person, InstitutionType
from .models import Institution,EventType,Image,Style,Figure,Event,DateType
from .models import Purpose,InstallationType,InstallationStatus, Installation,Literature
from .models import TextType, EventRole, LocType, Location
from .models import PersonSymbol, PersonType, ImageType

from django_select2.forms import ModelSelect2Widget, ModelSelect2MultipleWidget

names = 'original_name,ottoman_name,english_name,turkish_name'.split(',')

class DateTypeWidget(ModelSelect2Widget):
    model = DateType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return DateType.objects.all().order_by('name')


class EventTypeWidget(ModelSelect2Widget):
    model = EventType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return EventType.objects.all().order_by('name')


class EventWidget(ModelSelect2Widget):
    model = Event
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        label = obj.name
        if obj.start_date: 
            label += ' ' + str(obj.start_date.year)
        if obj.start_date and obj.end_date: 
            label += ' -'
        if obj.end_date: 
            label += ' ' + str(obj.end_date.year)
        return label 
    
    def get_queryset(self):
        return Event.objects.all().order_by('name')


class EventsWidget(ModelSelect2MultipleWidget):
    model = Event
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        label = obj.name
        if obj.start_date: 
            label += ' ' + str(obj.start_date.year)
            # EK: label += ' ' + str(obj.start_date.YEAR)
        if obj.start_date and obj.end_date: 
            label += ' -'
        if obj.end_date: 
            label += ' ' + str(obj.end_date.year)
            # EK: label += ' ' + str(obj.end_date.YEAR)
        return label 
    
    def get_queryset(self):
        return Event.objects.all().order_by('name')


class EventRoleWidget(ModelSelect2Widget):
    model = InstitutionType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return EventRole.objects.all().order_by('name')


class FigureWidget(ModelSelect2Widget):
    model = Figure
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Figure.objects.all().order_by('name')


class GenderWidget(ModelSelect2Widget):
    model = Gender
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Gender.objects.all().order_by('name')


class ImagesWidget(ModelSelect2MultipleWidget):
    model = Image
    search_fields = ['title__icontains']

    def label_from_instance(self,obj):
        return obj.title
    
    def get_queryset(self):
        return Image.objects.all().order_by('title')


class ImageTypeWidget(ModelSelect2Widget):
    model = ImageType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return ImageType.objects.all().order_by('name')


class ImageTypesWidget(ModelSelect2MultipleWidget):
    model = ImageType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return ImageType.objects.all().order_by('name')


class InstallationTypeWidget(ModelSelect2Widget):
    model = InstallationType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return InstallationType.objects.all().order_by('name')


class InstallationTypesWidget(ModelSelect2MultipleWidget):
    model = InstallationType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return InstallationType.objects.all().order_by('name')


class InstallationStatusWidget(ModelSelect2Widget):
    model = InstallationStatus
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return InstallationStatus.objects.all().order_by('name')


class InstallationStatusesWidget(ModelSelect2MultipleWidget):
    model = InstallationStatus
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return InstallationStatus.objects.all().order_by('name')


class InstallationWidget(ModelSelect2Widget):
    model = System
    # search_fields = [x + '__icontains' for x in names]
    search_fields = ['english_name__icontains']
    
    def label_from_instance(self,obj):
        return obj.english_name

    def get_queryset(self):
        return Installation.objects.all().order_by('english_name')


class InstitutionTypeWidget(ModelSelect2Widget):
    model = InstitutionType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return InstitutionType.objects.all().order_by('name')


class InstitutionWidget(ModelSelect2Widget):
    model = Person
    # search_fields = [x + '__icontains' for x in names]
    search_fields = ['english_name__icontains']

    def label_from_instance(self,obj):
        return obj.english_name
    
    def get_queryset(self):
        return Institution.objects.all().order_by('english_name')


class InstitutionsWidget(ModelSelect2MultipleWidget):
    model = Institution
    # search_fields = [x + '__icontains' for x in names]
    search_fields = ['english_name__icontains']
    
    def label_from_instance(self,obj):
        return obj.english_name

    def get_queryset(self):
        return Institution.objects.all().order_by('english_name')


class LiteratureWidget(ModelSelect2Widget):
    model = Literature
    search_fields = ['title__icontains','code__icontains']

    def label_from_instance(self,obj):
        return obj.code + ' | ' + obj.title
    
    def get_queryset(self):
        return Literature.objects.all().order_by('code')


class LocationWidget(ModelSelect2Widget):
    model = Location
    search_fields = ['name__icontains', 'loctype__name__icontains', 'x_coordinate', 'y_coordinate']

    def label_from_instance(self,obj):
        sName = "-" if obj.name is None else obj.name
        sType = "" if obj.loctype is None else " ({})".format(obj.loctype.name)
        sLabel = "{}: [{},{}]{}".format(sName, obj.x_coordinate, obj.y_coordinate, sType)
        return sLabel
    
    def get_queryset(self):
        return Location.objects.all().order_by('name', 'x_coordinate', 'y_coordinate')


class LocTypeWidget(ModelSelect2Widget):
    model = LocType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return LocType.objects.all().order_by('name')


class PersonWidget(ModelSelect2Widget):
    model = Person
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Person.objects.all().order_by('name')


class PersonsWidget(ModelSelect2MultipleWidget):
    model = Person
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Person.objects.all().order_by('name')


class PersonSymbolWidget(ModelSelect2Widget):
    model = PersonSymbol
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return PersonSymbol.objects.all().order_by('name')


class PersonSymbolsWidget(ModelSelect2MultipleWidget):
    model = PersonSymbol
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return PersonSymbol.objects.all().order_by('name')


class PersonTypeWidget(ModelSelect2Widget):
    model = PersonType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return PersonType.objects.all().order_by('name')


class PurposeWidget(ModelSelect2Widget):
    model = Purpose
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Purpose.objects.all().order_by('name')


class PurposesWidget(ModelSelect2MultipleWidget):
    model = Purpose
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Purpose.objects.all().order_by('name')


class ReligionWidget(ModelSelect2Widget):
    model = Religion
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Religion.objects.all().order_by('name')


class StyleWidget(ModelSelect2Widget):
    model = Style
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return Style.objects.all().order_by('name')
    

class SystemWidget(ModelSelect2Widget):
    model = System
    # search_fields = [x + '__icontains' for x in names]
    search_fields = ['english_name__icontains']
    
    def label_from_instance(self,obj):
        return obj.english_name

    def get_queryset(self):
        return System.objects.all().order_by('english_name')


class SystemsWidget(ModelSelect2MultipleWidget):
    model = System
    search_fields = ['english_name__icontains']

    def label_from_instance(self,obj):
        return obj.english_name
    
    def get_queryset(self):
        return System.objects.all().order_by('english_name')


class TextTypeWidget(ModelSelect2Widget):
    model = TextType
    search_fields = ['name__icontains']

    def label_from_instance(self,obj):
        return obj.name
    
    def get_queryset(self):
        return TextType.objects.all().order_by('name')



