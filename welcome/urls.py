from . import views
from django.urls import path

urlpatterns = [
    path('', views.Welcome.as_view(), name='home'),
    ]
