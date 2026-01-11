from django.urls import path
from . import views

# This app_name should match the namespace in your main urls.py
app_name = 'treeinvs' 

urlpatterns = [
    # This results in localhost:8000/etl/ <= configs.urls
    # path(endPoint, views.logic, variableName in html)
    path('', views.import_tree_csv, name='importCsv'),
    path('export-csv/', views.export_trees_csv, name='exportCsv'), # Add this ，Name: Used in HTML (e.g., {% url 'treeinvs:export_trees_csv' %}).

]