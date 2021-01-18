from django.urls import path
from clustering import views

urlpatterns = [
    path('cluster', views.cluster, name='hello_world'),
    path('', views.file_picker, name="filepicker")
]