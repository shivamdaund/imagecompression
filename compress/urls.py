from django.urls import path
from .views import compress_image

urlpatterns = [
    path('', compress_image, name='compress_image'),
]
