from . import views
from django.urls import path

urlpatterns = [
    path('add_product/', views.ProductAddView.as_view(), name='add_product'),
    path('update_product/<int:pk>', views.ProductUpdateView.as_view(),
         name='update_product'),
    ]
