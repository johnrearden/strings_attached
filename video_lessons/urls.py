from . import views
from django.urls import path

urlpatterns = [
    path('all_lessons/', views.AllLessonsView.as_view(),
         name='all_lessons'),
    path('video_player/<int:id>', views.VideoPlayer.as_view(),
         name='video_player'),
    path('subscribe/', views.SubscriptionOptionsView.as_view(),
         name='subscribe'),
    path('create_checkout_session/<int:subscription_id>',
         views.CreateStripeCheckoutSessionView.as_view(),
         name='create_subscription_checkout_session'),
    ]
