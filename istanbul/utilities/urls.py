from django.urls import include,path,re_path

from . import views


app_name = 'utilities'
urlpatterns = [
	# path('overview/',views.overview,name='overview'),
	path('close/',views.close,name='close'),
	path('list_view/<str:model_name>/<str:app_name>/',views.list_view,
		name='list_view'),
	path('list_view/<str:model_name>/<str:app_name>/<int:max_entries>',
		views.list_view, name='list_view'),
	path('delete_model/<int:pk>/<str:model_name>/<str:app_name>',
		views.delete_model,name='delete_model'),
]
