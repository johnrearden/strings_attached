from . import views
from django.urls import path

urlpatterns = [
    path('', views.ProductDisplay.as_view(), name='product_display'),
    path('<int:pk>/', views.ProductDetail.as_view(), name='product_detail'),
    ]
