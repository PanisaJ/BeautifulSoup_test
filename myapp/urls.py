from django.urls import path
from . import views 

urlpatterns = [
    path('', views.index, name = 'index'),
    path('get/', views.get_input, name = 'get_data' ),
    path('search/', views.search_data, name = 'search_data' ),
]
