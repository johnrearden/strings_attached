from . import views
from django.urls import path

urlpatterns = [
    path('', views.ProductDisplay.as_view(), name='product_display'),
    ]
