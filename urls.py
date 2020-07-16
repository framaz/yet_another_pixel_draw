from django.urls import path

from . import views

urlpatterns = [
    path('change_color/', views.UpdatePixel.as_view(), name='change_color'),
    path('upload_picture/', views.UploadPicture.as_view(), name='upload_picture'),
    path('get_from_grid/', views.GetPixelFromGrid.as_view(), name='get_from_grid')
]
