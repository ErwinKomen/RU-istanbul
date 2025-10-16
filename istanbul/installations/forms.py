"""
Forms for the Installations app inside istanbul-su
"""
from xml.dom import ValidationErr
from django import forms
from django.core.exceptions import ValidationError
from .models import System, Religion, Gender, Person, InstitutionType
from .models import Institution,EventType,Image,ImageType,Style,Figure,Event
from .models import Purpose,InstallationType,InstallationStatus,Installation,Literature
from .models import SystemInstallationRelation,TextType,DateType
from .models import EventLiteratureRelation, EventRole, InstitutionType
from .models import EventInstitutionRelation,EventPersonRelation
from .models import Location, LocType
from .models import PersonSymbol, PersonType
from .models import ExternalLink


from .widgets import SystemWidget, ReligionWidget, GenderWidget, PersonsWidget
from .widgets import InstitutionTypeWidget,InstitutionsWidget,ImagesWidget
from .widgets import InstitutionWidget, EventRoleWidget
from .widgets import EventTypeWidget,StyleWidget,FigureWidget, DateTypeWidget
from .widgets import InstallationTypeWidget,InstallationStatusWidget,InstallationWidget
from .widgets import InstallationTypesWidget,InstallationStatusesWidget
from .widgets import TextTypeWidget,LiteratureWidget,PurposesWidget
from .widgets import EventWidget, EventsWidget, PersonWidget
from .widgets import LocTypeWidget, LocationWidget, SystemsWidget
from .widgets import PersonSymbolWidget, PersonSymbolsWidget, PersonTypeWidget
from .widgets import ImageTypeWidget, ImageTypesWidget

# From our own application
from utils.select2 import  make_select2_attr
from utils.view_util import partial_year_to_date
from basic.utils import ErrHandle


dattr = {'attrs':{'style':'width:100%', 'class': 'searching'}}
dchar = {'widget':forms.TextInput(**dattr),'required':False}
dchar_required = {'widget':forms.TextInput(**dattr),'required':True}
dtext = {'widget':forms.Textarea(attrs={'style':'width:100%','rows':3}),
	'required':False}
dgps = {'widget':forms.NumberInput(**dattr), 'required':False}
dnumber= {'widget':forms.NumberInput(attrs={'style':'width:100%','rows':3}),
	'required':False}
dselect2 = make_select2_attr(input_length = 0)
dselect2n2 = make_select2_attr(input_length = 2)


# ================================= Main forms ===============================================

class SystemForm(forms.ModelForm):
	original_name = forms.CharField(**dchar)
	ottoman_name = forms.CharField(**dchar)
	english_name = forms.CharField(**dchar_required)
	turkish_name = forms.CharField(**dchar)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)
	location = forms.ModelChoiceField(
		queryset = Location.objects.all(),
		widget = LocationWidget(**dselect2),
		required = False)

	class Meta:
		model = System
		fields = 'original_name,ottoman_name,english_name,turkish_name'
		fields += ',description,comments,location'
		fields = fields.split(',')


class InstallationForm(forms.ModelForm):
	original_name = forms.CharField(**dchar)
	ottoman_name = forms.CharField(**dchar)
	english_name = forms.CharField(**dchar_required)
	turkish_name = forms.CharField(**dchar)
	installation_type = forms.ModelChoiceField(
		queryset = InstallationType.objects.all(),
		widget = InstallationTypeWidget(**dselect2),
		required = False)
	installation_status = forms.ModelChoiceField(
		queryset = InstallationStatus.objects.all(),
		widget = InstallationStatusWidget(**dselect2),
		required = False)
	events = forms.ModelMultipleChoiceField(
		queryset = Event.objects.all(),
		widget = EventsWidget(**dselect2),
		required = False)
	location = forms.ModelChoiceField(
		queryset = Location.objects.all(),
		widget = LocationWidget(**dselect2),
		required = False)
	purposes = forms.ModelMultipleChoiceField(
		queryset = Purpose.objects.all(),
		widget = PurposesWidget(**dselect2),
		required = False)
	images = forms.ModelMultipleChoiceField(
		queryset = Image.objects.all(),
		widget = ImagesWidget(**dselect2),
		required = False)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = Installation
		fields = 'original_name,ottoman_name,english_name,turkish_name'
		fields += ',installation_type,installation_status,events,purposes,description,comments'
		fields += ',still_exists,images,location'
		fields = fields.split(',')


class InstallationSearchForm(forms.ModelForm):
	english_name = forms.CharField(**dchar)
	itypelist = forms.ModelMultipleChoiceField(
		queryset = InstallationType.objects.all(),
		widget = InstallationTypesWidget(**dselect2),
		required = False)
	istatuslist = forms.ModelMultipleChoiceField(
		queryset = InstallationStatus.objects.all(),
		widget = InstallationStatusesWidget(**dselect2),
		required = False)
	eventlist = forms.ModelMultipleChoiceField(queryset = Event.objects.all(),widget = EventsWidget(**dselect2),required = False)
	purplist = forms.ModelMultipleChoiceField(queryset = Purpose.objects.all(),widget = PurposesWidget(**dselect2),required = False)
	perslist = forms.ModelMultipleChoiceField(required=False,queryset=Person.objects.all(),widget = PersonsWidget(**dselect2))
	systemlist = forms.ModelMultipleChoiceField(queryset = System.objects.all(),widget = SystemsWidget(**dselect2),required = False)
	start_date = forms.CharField(label="Date start", required=False, 
			widget=forms.TextInput(attrs={'placeholder': 'Starting from...',  'style': 'width: 30%;', 'class': 'searching'}))
	end_date = forms.CharField(label="Date end", required=False, 
			widget=forms.TextInput(attrs={'placeholder': 'Until (including)...',  'style': 'width: 30%;', 'class': 'searching'}))

	class Meta:
		model = Installation
		fields = ['english_name']


class PersonForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	gender = forms.ModelChoiceField(
		queryset = Gender.objects.all(),
		widget = GenderWidget(**dselect2),
		required = False)
	religion = forms.ModelChoiceField(
		queryset = Religion.objects.all(),
		widget = ReligionWidget(**dselect2),
		required = False)
	ptype = forms.ModelChoiceField(
		queryset = PersonType.objects.all().order_by('name'),
		widget = PersonTypeWidget(**dselect2),
		required = False)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = Person
		fields = 'name,gender,birth_year,death_year,start_reign,end_reign'
		fields += ',religion,ptype,description,comments'
		fields = fields.split(',')

	def save(self, commit=True, *args, **kwargs):
		# Get the instance
		instance = self.instance
		# Adapt the form.instance for date fields
		partial_year_to_date(self, instance, "start_reign", "start_reign")
		partial_year_to_date(self, instance, "end_reign", "end_reign")
		partial_year_to_date(self, instance, "birth_year", "birth_year")
		partial_year_to_date(self, instance, "death_year", "death_year")
		# Perform the actual saving
		response = super(PersonForm, self).save(commit=commit)
		# Return the save response
		return response


class LocationForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	loctype = forms.ModelChoiceField(
		queryset = LocType.objects.all(),
		widget = LocTypeWidget(**dselect2),
		required = False)
	x_coordinate = forms.CharField(required=False, 
		widget=forms.TextInput(attrs={'style':'width:50%', 'placeholder': 'Provide the x-coordinate (latitude)'}))
	y_coordinate = forms.CharField(required=False, 
		widget=forms.TextInput(attrs={'style':'width:50%', 'placeholder': 'Provide the y-coordinate (longitude)'}))

	class Meta:
		model = Location
		fields = 'name,loctype,x_coordinate,y_coordinate'
		fields = fields.split(',')

	def save(self, commit=True, *args, **kwargs):
		# Get the instance
		instance = self.instance
		# Perform the actual saving
		response = super(LocationForm, self).save(commit=commit)
		# Return the save response
		return response


class InstitutionForm(forms.ModelForm):
	original_name = forms.CharField(**dchar)
	ottoman_name = forms.CharField(**dchar)
	english_name = forms.CharField(**dchar_required)
	turkish_name = forms.CharField(**dchar)
	institution_type = forms.ModelChoiceField(
		queryset = InstitutionType.objects.all(),
		widget = InstitutionTypeWidget(**dselect2),
		required = False)
	religion = forms.ModelChoiceField(
		queryset = Religion.objects.all(),
		widget = ReligionWidget(**dselect2),
		required = False)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = Institution
		fields = 'original_name,ottoman_name,english_name,turkish_name'
		fields += ',institution_type,religion,description,comments'
		fields = fields.split(',')


class ReligionForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = Religion
		fields = 'name,description,comments'.split(',')


class EventForm(forms.ModelForm):
	# name = forms.CharField(**dchar_required)
	# event_type = forms.ModelChoiceField(queryset = EventType.objects.all(),
	# 	widget = EventTypeWidget(**dselect2),required = False)
	# date_comments = forms.CharField(**dtext)
	# #images = forms.ModelMultipleChoiceField(
	# #	queryset = Image.objects.all(),
	# #	widget = ImagesWidget(**dselect2),
	# #	required = False)
	# end_date_type = forms.ModelChoiceField(queryset = DateType.objects.all(),
	# 	widget = DateTypeWidget(attrs={'style': 'width: 50%;', 'data-minimum-input-length': 0}),
	# 	required = False)
	# figure = forms.ModelChoiceField(queryset = Figure.objects.all(),
	# 	widget = FigureWidget(**dselect2),required = False)
	# description = forms.CharField(**dtext)
	# comments = forms.CharField(**dtext)

	class Meta:
		model = Event
		fields = 'name,start_date,end_date,end_date_type,date_comments' #,images'
		fields += ',figure,description,comments,event_type'
		fields = fields.split(',')
		widgets={
			'name':			forms.TextInput(**dattr),
			'event_type':	EventTypeWidget(**dselect2),
			'date_comments': forms.Textarea(attrs={'style':'width:100%','rows':3}),
			'end_date_type': DateTypeWidget(attrs={'style': 'width: 50%;', 'data-minimum-input-length': 0}),
			'figure':		FigureWidget(**dselect2),
			'description':	forms.Textarea(attrs={'style':'width:100%','rows':3}),
			'comments':		forms.Textarea(attrs={'style':'width:100%','rows':3}),
			}

	def __init__(self, *args, **kwargs):
        # Start by executing the standard handling
		super().__init__(*args, **kwargs)
		oErr = ErrHandle()
		try:
			# Some fields are not required
			self.fields['date_comments'].required = False
			self.fields['description'].required = False
			self.fields['comments'].required = False

		except:
			msg = oErr.get_error_message()
			oErr.DoError("EventForm-init")
		return None

	def save(self, commit=True, *args, **kwargs):
		# Get the instance
		instance = self.instance
		# Adapt the form.instance for start_date and end_date
		partial_year_to_date(self, instance, "start_date", "start_date")
		partial_year_to_date(self, instance, "end_date", "end_date")
		# Perform the actual saving
		response = super(EventForm, self).save(commit=commit)

		# If this is that actual committing, then process after-save stuff
		if commit:
			instance.order_events()

		# Return the save response
		return response

	def clean_start_date(self):
		data = self.cleaned_data.get("start_date")
		if data:
			# Try converting into integer
			try:
				idata = int(data)
			except:
				# Data should be integer
				raise ValidationError("Start date must be an integer")
			# Continue test if integer
			if idata < 0:
				raise ValidationError("Start date may not be negative")

		# If all went well
		return data

	def clean_end_date(self):
		data = self.cleaned_data.get("end_date")
		if data:
			# Try converting into integer
			try:
				end_date = int(data)
			except:
				# Data should be integer
				raise ValidationError("End date must be an integer")
			# Continue test if integer
			if end_date < 0:
				raise ValidationError("End date may not be negative")
			# Check if end date is higher than start date
			start = self.cleaned_data.get("start_date")
			if start:
				try:
					start_date = int(start)
				except:
					# no more errors
					i = 1
				# Compare
				if start_date > end_date:
					raise ValidationError("End date may not be before the start date")
		# If all went well
		return data


class LiteratureForm(forms.ModelForm):
	code = forms.CharField(**dchar_required)
	title= forms.CharField(**dchar_required)
	author= forms.CharField(**dchar)
	editor= forms.CharField(**dchar)
	publisher= forms.CharField(**dchar)
	place= forms.CharField(**dchar)
	year= forms.CharField(**dchar)
	journal= forms.CharField(**dchar)
	volume= forms.CharField(**dchar)
	page_numbers= forms.CharField(**dchar)
	issue= forms.CharField(**dchar)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)
	
	class Meta:
		model = Literature
		fields = 'code,title,author,editor'
		fields += ',publisher,place,year,journal,volume'
		fields += ',page_numbers,issue,description,comments'
		fields = fields.split(',')


# ================================= Helper model forms ========================================


class EventRoleForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)

	class Meta:
		model = EventRole
		fields = ['name']


class EventTypeForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = EventType
		fields = 'name,description,comments'.split(',')


class FigureForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	style = forms.ModelChoiceField(
		queryset = Style.objects.all(),
		widget = StyleWidget(**dselect2),
		required = False)

	class Meta:
		model = Figure 
		fields = 'name,geojson,style'.split(',')


class GenderForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)

	class Meta:
		model = Gender
		fields = ['name']


class ImageForm(forms.ModelForm):
	maker = forms.CharField(**dchar)
	title = forms.CharField(**dchar)
	url= forms.CharField(**dchar)
	current_location= forms.CharField(**dchar)
	collection = forms.CharField(**dchar)
	itype = forms.ModelChoiceField(
		queryset = ImageType.objects.all().order_by('name'),
		widget = ImageTypeWidget(**dselect2),
		required = False)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = Image
		fields = 'image_file,maker,year,title,url,current_location'
		fields += ',itype,collection,description,comments'		
		fields = fields.split(',')

	def save(self, commit=True, *args, **kwargs):
		# Get the instance
		instance = self.instance
		# Adapt the form.instance for date fields
		partial_year_to_date(self, instance, "year", "year")
		# Perform the actual saving
		response = super(ImageForm, self).save(commit=commit)
		# Return the save response
		return response


class ImageSearchForm(ImageForm):
	itypelist = forms.ModelMultipleChoiceField(
		queryset = ImageType.objects.all().order_by('name'),
		widget = ImageTypesWidget(**dselect2),
		required = False)
	start_date = forms.CharField(label="Date start", required=False, 
			widget=forms.TextInput(attrs={'placeholder': 'Starting from...',  'style': 'width: 30%;', 'class': 'searching'}))
	end_date = forms.CharField(label="Date end", required=False, 
			widget=forms.TextInput(attrs={'placeholder': 'Until (including)...',  'style': 'width: 30%;', 'class': 'searching'}))


class InstallationTypeForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = InstallationType
		fields = 'name,description,comments'.split(',')
	

class InstitutionTypeForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = InstallationType
		fields = 'name,description,comments'.split(',')


class PersonSymbolForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = PersonSymbol
		fields = 'name,description,comments'.split(',')


class PersonSymbolSearchForm(PersonSymbolForm):

    def __init__(self, *args, **kwargs):
        # Start by executing the standard handling
        super(PersonSymbolSearchForm, self).__init__(*args, **kwargs)

        # Some fields are not required
        self.fields['name'].required = False

        # We do not really return anything from the init
        return None


class PersonTypeForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	symbol = forms.ModelChoiceField(
		queryset = PersonSymbol.objects.all().order_by('name'),
		widget = PersonSymbolWidget(**dselect2),
		required = False)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = PersonType
		fields = 'name,symbol,description,comments'.split(',')


class PersonTypeSearchForm(PersonTypeForm):
	symbollist = forms.ModelMultipleChoiceField(
		queryset = PersonSymbol.objects.all().order_by('name'),
		widget = PersonSymbolsWidget(**dselect2),
		required = False)

	def __init__(self, *args, **kwargs):
		# Start by executing the standard handling
		super(PersonTypeSearchForm, self).__init__(*args, **kwargs)

        # Some fields are not required
		self.fields['name'].required = False

        # We do not really return anything from the init
		return None


class PurposeForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = Purpose
		fields = 'name,description,comments'.split(',')


class StyleForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)
	line_thickness = forms.IntegerField(**dnumber)
	fill_opacity = forms.FloatField(**dnumber)
	line_opacity = forms.FloatField(**dnumber)
	z_index = forms.IntegerField(**dnumber)

	class Meta:
		model = Style
		fields = 'name,color,line_thickness,fill_opacity,line_opacity'
		fields += ',dashed,z_index'
		fields = fields.split(',')
	

class TextTypeForm(forms.ModelForm):
	name = forms.CharField(**dchar_required)

	class Meta:
		model = TextType
		fields = ['name']


# ================================== Relation forms ==========================================

class SystemInstallationRelationForm(forms.ModelForm):
	system = forms.ModelChoiceField(
		queryset = System.objects.all(),
		widget = SystemWidget(**dselect2),
		required = False)
	installation= forms.ModelChoiceField(
		queryset = Installation.objects.all(),
		widget = InstallationWidget(**dselect2),
		required = False)
	description = forms.CharField(**dtext)
	comments = forms.CharField(**dtext)

	class Meta:
		model = SystemInstallationRelation
		fields = 'system,installation,start_date,end_date'
		fields += ',description,comments,is_part_of'
		fields = fields.split(',')

	def save(self, commit=True, *args, **kwargs):
		# Get the instance
		instance = self.instance
		# Adapt the form.instance for date fields
		partial_year_to_date(self, instance, "start_date", "start_date")
		partial_year_to_date(self, instance, "end_date", "end_date")
		# Perform the actual saving
		response = super(SystemInstallationRelationForm, self).save(commit=commit)
		# Return the save response
		return response


class EventLiteratureRelationForm(forms.ModelForm):
	event = forms.ModelChoiceField(
		queryset = Event.objects.all(),
		widget = EventWidget(**dselect2),
		required = False)
	literature = forms.ModelChoiceField(
		queryset = Literature.objects.all(),
		widget = LiteratureWidget(**dselect2),
		required = False)
	page_number= forms.CharField(**dchar)
	text = forms.CharField(**dtext)
	text_type = forms.ModelChoiceField(
		queryset = TextType.objects.all(),
		widget = TextTypeWidget(**dselect2),
		required = False)

	class Meta:
		model = EventLiteratureRelation
		fields = 'event,literature,page_number,text'
		fields += ',text_file,text_type'
		fields = fields.split(',')


class EventInstitutionRelationForm(forms.ModelForm):
	event = forms.ModelChoiceField(
		queryset = Event.objects.all(),
		widget = EventWidget(**dselect2),
		required = False)
	institution= forms.ModelChoiceField(
		queryset = Institution.objects.all(),
		widget = InstitutionWidget(**dselect2),
		required = False)
	role = forms.ModelChoiceField(
		queryset = EventRole.objects.all(),
		widget = EventRoleWidget(**dselect2),
		required = False)

	class Meta:
		model = EventInstitutionRelation
		fields = 'event,institution,role'
		fields = fields.split(',')


class EventPersonRelationForm(forms.ModelForm):
	event = forms.ModelChoiceField(
		queryset = Event.objects.all(),
		widget = EventWidget(**dselect2),
		required = False)
	person= forms.ModelChoiceField(
		queryset = Person.objects.all(),
		widget = PersonWidget(**dselect2),
		required = False)
	role = forms.ModelChoiceField(
		queryset = EventRole.objects.all(),
		widget = EventRoleWidget(**dselect2),
		required = False)

	class Meta:
		model = EventPersonRelation
		fields = 'event,person,role'
		fields = fields.split(',')


class ExternalLinkForm(forms.ModelForm):
	installation= forms.ModelChoiceField(
		queryset = Installation.objects.all(),
		widget = InstallationWidget(**dselect2),
		required = False)
	name = forms.CharField(**dchar_required)
	url = forms.URLField(**dchar)

	class Meta:
		model = ExternalLink
		fields = 'installation,name,url'
		fields = fields.split(",")


# ================================= Formsets ===============================================

systeminstallation_formset = forms.inlineformset_factory(
	System,SystemInstallationRelation,
	form = SystemInstallationRelationForm, extra = 1)
installationsystem_formset = forms.inlineformset_factory(
	Installation,SystemInstallationRelation,
	form = SystemInstallationRelationForm, extra = 1)

eventliterature_formset = forms.inlineformset_factory(
	Event,EventLiteratureRelation,
	form = EventLiteratureRelationForm, extra = 1)
literatureevent_formset = forms.inlineformset_factory(
	Literature,EventLiteratureRelation,
	form = EventLiteratureRelationForm, extra = 1)

eventinstitution_formset = forms.inlineformset_factory(
	Event,EventInstitutionRelation,
	form = EventInstitutionRelationForm, extra = 1)
institutionevent_formset = forms.inlineformset_factory(
	Institution,EventInstitutionRelation,
	form = EventInstitutionRelationForm, extra = 1)

eventperson_formset = forms.inlineformset_factory(
	Event,EventPersonRelation,
	form = EventPersonRelationForm, extra = 1)
personevent_formset = forms.inlineformset_factory(
	Person,EventPersonRelation,
	form = EventPersonRelationForm, extra = 1)

installationextlink_formset = forms.inlineformset_factory(
	Installation,ExternalLink,
	form = ExternalLinkForm, extra = 1)

