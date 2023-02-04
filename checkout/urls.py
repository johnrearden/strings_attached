from . import views
from django.urls import path

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    path('save_order/', views.SaveOrderView.as_view(), name='save_order'),
    path('payment_confirmed/', views.PaymentConfirmed.as_view(),
         name='payment_confirmed'),
    path('checkout_success/', views.CheckoutSuccess.as_view(),
         name='checkout_success'),
    ]
