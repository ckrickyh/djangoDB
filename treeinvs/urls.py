from django.urls import path
from . import views

# This app_name should match the namespace in your main urls.py
app_name = 'treeinvs' 

urlpatterns = [
    # This results in localhost:8000/etl/
    path('', views.etl, name='etl'), 
]