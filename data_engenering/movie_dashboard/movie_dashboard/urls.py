# movie_dashboard/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add this line to include urls from our dashboard app
    path('', include('dashboard.urls')),
]