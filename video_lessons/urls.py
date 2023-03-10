from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('all_lessons/', views.AllLessonsView.as_view(),
         name='all_lessons'),
    path('video_player/<int:id>', views.VideoPlayer.as_view(),
         name='video_player'),
    path('subscribe/', login_required(views.SubscriptionOptionsView.as_view()),
         name='subscribe'),
    path('create_checkout_session/<int:subscription_id>',
         login_required(views.CreateStripeCheckoutSessionView.as_view()),
         name='create_subscription_checkout_session'),
    path('subscription_success/', views.SubscriptionSuccessView.as_view(),
         name='subscription_success'),
    ]
