from . import views
from django.urls import path

urlpatterns = [
    path('view_basket/', views.ViewBasket.as_view(), name='view_basket'),
    path('add_to_basket/', views.AddToBasket.as_view(), name='add_to_basket'),
    ]
