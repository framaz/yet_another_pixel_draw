from django.urls import path

from . import views

urlpatterns = [
    path('change_color/', views.UpdatePixel.as_view(), name='change_color'),
    path('upload_picture/', views.UploadPicture.as_view(), name='upload_picture'),
    path('grid/<int:size>/<int:x>/<int:y>/', views.GetPixelFromGrid.as_view(), name='get_from_grid'),
    path('grid/', views.GetGridSize.as_view(), name='get_grid_size'),
    path('history/', views.GetHistory.as_view(), name='get_history'),
    path('', views.FrontEnd.as_view(), name="frontend")
]
