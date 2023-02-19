from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from .models import LessonSeries, VideoLesson, UserLearningProfile,\
     Subscription
import stripe


class AllLessonsView(View):
    def get(self, request):

        # Check if the user is a paid up subscriber.
        full_access = False
        if not request.user.is_anonymous:
            profile = UserLearningProfile.objects.filter(user=request.user)
            if profile:
                subscriber = profile[0].subscriber 
                paid = profile[0].subscription_paid
                full_access = subscriber and paid

        context = {
            'series': [],
            'full_access': full_access}
        series = LessonSeries.objects.all()
        for ser in series:
            lessons = VideoLesson.objects.filter(series=ser)\
                                         .order_by('ordinal')
            lesson_count = len(lessons) if full_access else \
                settings.FREE_LESSONS
            context['series'].append({
                'name': ser.name,
                'lessons': lessons,
                'description': ser.description,
                'full_access': full_access,
                'lesson_count': lesson_count,
            })
        return render(request, 'video_lessons/all_lessons.html', context)


class VideoPlayer(View):
    def get(self, request, id):
        # Check if the user is a paid up subscriber.
        full_access = False
        if not request.user.is_anonymous:
            profile = UserLearningProfile.objects.filter(user=request.user)
            if profile:
                subscriber = profile[0].subscriber 
                paid = profile[0].subscription_paid
                full_access = subscriber and paid

        lesson = VideoLesson.objects.get(pk=id)
        series = lesson.series
        lessons = VideoLesson.objects.filter(series=series)
        lesson_count = len(lessons) if full_access else settings.FREE_LESSONS
        context = {
            'lesson': lesson,
            'lessons_in_series': lessons,
            'lesson_count': lesson_count,
            'full_access': full_access,
        }
        return render(request, 'video_lessons/video_player.html', context)


class SubscriptionOptionsView(View):
    def get(self, request):
        subscriptions = Subscription.objects.all().order_by('ordinal')
        context = {
            'subscriptions': subscriptions,
        }
        return render(request, 'video_lessons/subscribe.html', context)


class CreateStripeCheckoutSessionView(View):
    def get(self, request, subscription_id):
        subscription = Subscription.objects.get(pk=subscription_id)
        stripe_lookup_id = subscription.stripe_lookup_id
        stripe.api_key = settings.STRIPE_PRIVATE_KEY
        session = stripe.checkout.Session.create(
            success_url='https://localhost:8000/',
            cancel_url='https://localhost:8000/',
            mode='subscription',
            line_items=[{
                'price': stripe_lookup_id,
                'quantity': 1,
            }],
        )
        return redirect(session.url)
