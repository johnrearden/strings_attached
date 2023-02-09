from . import views
from django.urls import path

urlpatterns = [
    path('add_product/', views.ProductAddView.as_view(), name='add_product'),
    path('update_product/<int:pk>', views.ProductUpdateView.as_view(),
         name='update_product'),
    path('staff_product_list/<str:sort_key>', views.StaffProductList.as_view(),
         name='staff_product_list'),
    ]
