from . import views
from django.urls import path

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    path('save_order/', views.SaveOrderView.as_view(), name='save_order'),
    path('payment_confirmed/', views.PaymentConfirmedView.as_view(),
         name='payment_confirmed'),
    path('checkout_success/', views.CheckoutSuccessView.as_view(),
         name='checkout_success'),
    ]
