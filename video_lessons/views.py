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

        # If no user_learning_profile exists, create one (login is required
        # for this view, so the user will not be anonymous)
        user_learning_profile = UserLearningProfile.objects.\
            filter(user=request.user)
        if not user_learning_profile:
            profile = UserLearningProfile.objects.create(
                user=request.user,
            )
        else:
            profile = user_learning_profile[0]
        subscription = Subscription.objects.get(pk=subscription_id)
        stripe_lookup_id = subscription.stripe_lookup_id
        stripe.api_key = settings.STRIPE_PRIVATE_KEY
        metadata = {
            'user_id': profile.id,
        }
        base_url = 'http://localhost:8000'
        email = request.user.email
        session = stripe.checkout.Session.create(
            success_url=f'{base_url}/video_lessons/subscription_success/',
            cancel_url=f'{base_url}/video_lessons/subscription_cancelled/',
            mode='subscription',
            currency=settings.STRIPE_CURRENCY,
            line_items=[{
                'price': stripe_lookup_id,
                'quantity': 1,
            }],
            customer_email=email,
            metadata=metadata,
        )
        print(session.last_response.body)
        return redirect(session.url)


class SubscriptionSuccessView(View):
    def get(self, request):
        return render(request, 'video_lessons/subscription_success.html')


class SubscriptionCancelledView(View):
    def get(self, request):
        return render(request, 'video_lessons/subscription_cancelled.html')
