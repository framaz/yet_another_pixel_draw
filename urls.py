from django.urls import path

from . import views

urlpatterns = [
    path('change_color', views.UpdatePixel.as_view(), name='change_color'),
]
