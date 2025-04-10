from django.urls import include, path, re_path
from . import views

app_name = 'installations'

urlpatterns = [
	path('',views.home, name = 'home'),
	path('home/',views.home, name = 'home'),
	path('contact/', views.contact, name='contact'),
	path('about/', views.about, name='about'),

	# ================== Detail View ===================================
    path('detail_installation_view/<int:pk>/', views.detail_installation_view, name='detail_installation_view'),

	# ================== Add ====================================
	path('add_system/',views.edit_system, name = 'add_system'),
	path('add_system/<str:view>', views.edit_system, name = 'add_system'),

	path('add_installation/',views.edit_installation, name = 'add_installation'),
	path('add_installation/<str:view>', views.edit_installation, name = 'add_installation'),

	path('add_person/',views.edit_person, name = 'add_person'),
	path('add_person/<str:view>', views.edit_person, name = 'add_person'),

	path('add_institution/',views.edit_institution, name = 'add_institution'),
	path('add_institution/<str:view>',views.edit_institution, name = 'add_institution'),

	path('add_institutiontype/',views.edit_institutiontype, name = 'add_institutiontype'),
	path('add_institutiontype/<str:view>',views.edit_institutiontype, name = 'add_institutiontype'),

	path('add_installationtype/',views.edit_installationtype, name = 'add_installationtype'),
	path('add_installationtype/<str:view>',views.edit_installationtype, name = 'add_installationtype'),

	path('add_eventtype/',views.edit_eventtype, name = 'add_eventtype'),
	path('add_eventtype/<str:view>',views.edit_eventtype, name = 'add_eventtype'),

	path('add_purpose/',views.edit_purpose, name = 'add_purpose'),
	path('add_purpose/<str:view>',views.edit_purpose, name = 'add_purpose'),

	path('add_texttype/',views.edit_texttype, name = 'add_texttype'),
	path('add_texttype/<str:view>',views.edit_texttype, name = 'add_texttype'),

	path('add_eventrole/',views.edit_eventrole, name = 'add_eventrole'),
	path('add_eventrole/<str:view>',views.edit_eventrole, name = 'add_eventrole'),

	path('add_religion/',views.edit_religion, name = 'add_religion'),
	path('add_religion/<str:view>',views.edit_religion, name = 'add_religion'),

	path('add_location/',views.edit_location, name = 'add_location'),
	path('add_location/<str:view>',views.edit_location, name = 'add_location'),

	path('add_event/',views.edit_event, name = 'add_event'),
	path('add_event/<str:view>', views.edit_event, name = 'add_event'),

	path('add_literature/',views.edit_literature, name = 'add_literature'),
	path('add_literature/<str:view>',views.edit_literature, name = 'add_literature'),

	path('add_image/',views.edit_image, name = 'add_image'),
	path('add_image/<str:view>',views.edit_image, name = 'add_image'),

	path('add_figure/',views.edit_figure, name = 'add_figure'),
	path('add_figure/<str:view>',views.edit_figure, name = 'add_figure'),

	path('add_style/',views.edit_style, name = 'add_style'),
	path('add_style/<str:view>',views.edit_style, name = 'add_style'),

	path('add_personsymbol/',views.edit_personsymbol, name = 'add_personsymbol'),
	path('add_personsymbol/<str:view>',views.edit_personsymbol, name = 'add_personsymbol'),

	path('add_persontype/',views.edit_persontype, name = 'add_persontype'),
	path('add_persontype/<str:view>',views.edit_persontype, name = 'add_persontype'),


	# ==================== EDIT =========================================
	path('edit_system/<int:pk>', views.edit_system, name = 'edit_system'),
	path('edit_system/<int:pk>/<str:focus>', views.edit_system, name = 'edit_system'),

	path('edit_event/<int:pk>', views.edit_event, name = 'edit_event'),
	path('edit_event/<int:pk>/<str:focus>', views.edit_event, name = 'edit_event'),

	path('edit_person/<int:pk>', views.edit_person, name = 'edit_person'),
	path('edit_person/<int:pk><str:focus>', views.edit_person, name = 'edit_person'),

	path('edit_installation/<int:pk>', views.edit_installation, name = 'edit_installation'),
	path('edit_installation/<int:pk>/<str:focus>', views.edit_installation, name = 'edit_installation'),

	path('edit_institution/<int:pk>', views.edit_institution, name = 'edit_institution'),
	path('edit_institution/<int:pk>/<str:focus>', views.edit_institution, name = 'edit_institution'),

	path('edit_literature/<int:pk>', views.edit_literature, name = 'edit_literature'),
	path('edit_literature/<int:pk>/<str:focus>', views.edit_literature, name = 'edit_literature'),

	path('edit_institutiontype/<int:pk>',views.edit_institutiontype, name = 'edit_institutiontype'),
	path('edit_institutiontype/<int:pk>/<str:focus>',views.edit_institutiontype, name = 'edit_institutiontype'),

	path('edit_installationtype/<int:pk>',views.edit_installationtype, name = 'edit_installationtype'),
	path('edit_installationtype/<int:pk>/<str:focus>',views.edit_installationtype, name = 'edit_installationtype'),

	path('edit_eventtype/<int:pk>',views.edit_eventtype, name = 'edit_eventtype'),
	path('edit_eventtype/<int:pk>/<str:focus>',views.edit_eventtype, name = 'edit_eventtype'),

	path('edit_purpose/<int:pk>',views.edit_purpose, name = 'edit_purpose'),
	path('edit_purpose/<int:pk>/<str:focus>',views.edit_purpose, name = 'edit_purpose'),

	path('edit_texttype/<int:pk>', views.edit_texttype, name = 'edit_texttype'),
	path('edit_texttype/<int:pk>/<str:focus>', views.edit_texttype, name = 'edit_texttype'),

	path('edit_eventrole/<int:pk>', views.edit_eventrole, name = 'edit_eventrole'),
	path('edit_eventrole/<int:pk>/<str:focus>', views.edit_eventrole, name = 'edit_eventrole'),

	path('edit_religion/<int:pk>', views.edit_religion, name = 'edit_religion'),
	path('edit_religion/<int:pk>/<str:focus>', views.edit_religion, name = 'edit_religion'),

	path('edit_location/<int:pk>', views.edit_location, name = 'edit_location'),
	path('edit_location/<int:pk>/<str:focus>', views.edit_location, name = 'edit_location'),

	path('edit_image/<int:pk>', views.edit_image, name = 'edit_image'),
	path('edit_image/<int:pk>/<str:focus>', views.edit_image, name = 'edit_image'),

	path('edit_figure/<int:pk>', views.edit_figure, name = 'edit_figure'),
	path('edit_figure/<int:pk>/<str:focus>', views.edit_figure, name = 'edit_figure'),

	path('edit_style/<int:pk>', views.edit_style, name = 'edit_style'),
	path('edit_style/<int:pk>/<str:focus>', views.edit_style, name = 'edit_style'),

	path('edit_personsymbol/<int:pk>',views.edit_personsymbol, name = 'edit_personsymbol'),
	path('edit_personsymbol/<int:pk>/<str:focus>',views.edit_personsymbol, name = 'edit_personsymbol'),

	path('edit_persontype/<int:pk>',views.edit_persontype, name = 'edit_persontype'),
	path('edit_persontype/<int:pk>/<str:focus>',views.edit_persontype, name = 'edit_persontype'),

]
