# project_name/urls.py (Contoh)

from django.contrib import admin
from django.urls import path, include 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('absensi_app.urls')), 
]