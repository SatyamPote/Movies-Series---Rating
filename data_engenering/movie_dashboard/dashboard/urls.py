# dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('download-csv/', views.download_csv, name='download_csv'),
    # NEW: URL route for JSON downloads
    path('download-json/', views.download_json, name='download_json'),
]