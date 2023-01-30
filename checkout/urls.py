from . import views
from django.urls import path

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    ]
