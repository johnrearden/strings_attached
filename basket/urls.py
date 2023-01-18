from . import views
from django.urls import path

urlpatterns = [
    path('view_basket/', views.ViewBasket.as_view(), name='view_basket'),
    path('add_to_basket/<str:product_id>', views.AddToBasket.as_view(),
         name='add_to_basket'),
    ]
