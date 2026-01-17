from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
  path('', views.index, name = 'indexInfo'),
  path('about', views.about, name='aboutInfo'),
]

# url.py 帶落 view.py