from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('query/', views.query_like_count, name='query_like_count'), # added the path
    path('export/', views.export_movie_csv, name='export_movie_csv'),  # Keep this
]