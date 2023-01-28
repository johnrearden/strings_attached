from . import views
from django.urls import path

urlpatterns = [
    path('view_basket/', views.ViewBasket.as_view(), name='view_basket'),
    path('add_to_basket/<str:product_id>', views.AddToBasket.as_view(),
         name='add_to_basket'),
    path('remove_from_basket/<str:product_id>',
         views.RemoveFromBasket.as_view(),
         name='remove_from_basket'),
    path('empty_basket/', views.EmptyBasket.as_view(), name="empty_basket"),
    path('replace_item_quantity/<str:product_id>',
         views.ReplaceItemQuantity.as_view(),
         name='replace_item_quantity'),
    ]
