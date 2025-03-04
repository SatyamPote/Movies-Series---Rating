from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('export/', views.export_movie_csv, name='export_movie_csv'),
]