from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect
from .models import LessonSeries, VideoLesson, UserLearningProfile,\
     Subscription
import stripe


class AllLessonsView(View):
    """
    This view returns a list of all of the lesson series, and all of the
    lessons they contain. It checks the user, first for anonymity, and then
    to ensure that they are both a subscriber and fully paid up. If these
    conditions are met, the full_access flag is set to True, otherwise the
    user will only be able to access the default number of free lessons set in
    settings.py.
    """
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
    """
    This view returns a page with a html video element that plays the
    requested video. As with the all lessons view, only logged in, subscribed
    and paid up members will have the full_access flag set to True
    """
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
        lessons = VideoLesson.objects.filter(series=series).order_by('ordinal')
        lesson_count = len(lessons) if full_access else settings.FREE_LESSONS
        context = {
            'lesson': lesson,
            'lessons_in_series': lessons,
            'lesson_count': lesson_count,
            'full_access': full_access,
        }
        return render(request, 'video_lessons/video_player.html', context)


class SubscriptionOptionsView(View):
    """
    This view displays the available subscription plans to the user.
    """
    def get(self, request):
        subscriptions = Subscription.objects.all().order_by('ordinal')
        context = {
            'subscriptions': subscriptions,
        }
        return render(request, 'video_lessons/subscribe.html', context)


class CreateStripeCheckoutSessionView(View):
    """
    This view creates a Stripe checkout session, passing it the lookup_id
    of the chosen subscription, the user's profile_id, success and
    cancellation urls and the user's email. It then redirects to the
    url provided by the Stripe checkout session.
    """
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
        base_url = settings.BASE_URL
        email = request.user.email
        session = stripe.checkout.Session.create(
            success_url=f'{base_url}/video_lessons/subscription_success/',
            mode='subscription',
            currency=settings.STRIPE_CURRENCY,
            line_items=[{
                'price': stripe_lookup_id,
                'quantity': 1,
            }],
            customer_email=email,
            metadata=metadata,
        )
        return redirect(session.url)


class SubscriptionSuccessView(View):
    """
    This view is redirected to by the Stripe checkout session, and provides
    links to the all_lessons display page, and via the post request below
    to the Stripe subscription management page.
    """
    def get(self, request):
        return render(request, 'video_lessons/subscription_success.html')

    def post(self, request):
        """
        This post method is called by a link on the page to enable the user
        to visit Stripe's subscription management portal, e.g. to change
        their payment details.
        """
        profile = get_object_or_404(UserLearningProfile, user=request.user)
        stripe.api_key = settings.STRIPE_PRIVATE_KEY
        base_url = settings.BASE_URL
        return_url = f'{base_url}{reverse("all_lessons")}'
        session = stripe.billing_portal.Session.create(
            customer=profile.stripe_customer_id,
            return_url=return_url,
        )
        return HttpResponseRedirect(session.url)
