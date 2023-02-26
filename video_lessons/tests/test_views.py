from django.test import TestCase
from django.contrib.auth.models import User
from video_lessons.views import *
from video_lessons.models import UserLearningProfile, LessonSeries,\
    VideoLesson, Subscription
from django.urls import reverse
import mock


class TestVideoLessonViews(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(
            username='name',
            password='pass',
            email='name@mail.com',
        )
        cls.profile = UserLearningProfile.objects.create(
            user=cls.user,
            subscriber=True,
            subscription_paid=True,
        )
        cls.lesson_series = LessonSeries.objects.create(
            name='test_lesson_series')
        cls.video_lesson = VideoLesson.objects.create(
            series=cls.lesson_series,
            name='test_video',
            ordinal=1,
            video_file='test_media_files/test_lesson_image',
            image='test_media_files/test_lesson_image'
        )
        cls.subscription = Subscription.objects.create(
            name='test_sub',
            price=20,
            description='description',
            image='test_media_files/test_subscription_image',
        )

    def test_all_lessons_view_template_and_status_code(self):
        response = self.client.get('/video_lessons/all_lessons/')
        self.assertTemplateUsed('video_lessons/all_lessons.html')
        self.assertEqual(response.status_code, 200)

    def test_all_lessons_view_grants_full_access_to_paid_up_subscriber(self):
        self.client.force_login(self.user)
        response = self.client.get('/video_lessons/all_lessons/')
        self.assertEqual(response.context['full_access'], True)

    def test_all_lessons_view_doesnt_grant_full_access_to_anonymous_user(self):
        # No forced login.
        response = self.client.get('/video_lessons/all_lessons/')
        self.assertEqual(response.context['full_access'], False)

    def test_no_full_access_for_subscriber_not_paid_up(self):
        temp_user = User.objects.create(username='Joe', password='x')
        UserLearningProfile.objects.create(user=temp_user, subscription_paid=False)
        self.client.force_login(temp_user)
        response = self.client.get('/video_lessons/all_lessons/')
        self.assertEqual(response.context['full_access'], False)

    def test_all_lessons_view_returns_all_available_series(self):
        series_count = len(LessonSeries.objects.all())
        response = self.client.get('/video_lessons/all_lessons/')
        self.assertEqual(len(response.context['series']), series_count)

    def test_video_player_template_and_status_code(self):
        id = self.video_lesson.pk
        response = self.client.get(f'/video_lessons/video_player/{id}')
        self.assertTemplateUsed('video_lessons/video_player.html')
        self.assertEqual(response.status_code, 200)

    def test_video_player_grants_full_access_to_paid_up_subscriber(self):
        self.client.force_login(self.user)
        id = self.video_lesson.pk
        response = self.client.get(f'/video_lessons/video_player/{id}')
        self.assertEqual(response.context['full_access'], True)

    def test_subscription_options_view_template_and_status_code(self):
        self.client.force_login(self.user)
        response = self.client.get('/video_lessons/subscribe/')
        self.assertTemplateUsed('video_lessons.subscribe.html')
        self.assertEqual(response.status_code, 200)

    def test_subscription_options_view_not_accessible_to_anonymous_user(self):
        response = self.client.get('/video_lessons/subscribe/')
        self.assertRedirects(
            response=response,
            expected_url=f'{reverse("account_login")}?next=/video_lessons/subscribe/')

    def test_anonymous_user_cant_access_create_stripe_checkout_session_view(self):
        sub_id = self.subscription.pk
        url = f'/video_lessons/create_checkout_session/{sub_id}'
        response = self.client.get(url)
        self.assertRedirects(
            response=response,
            expected_url=f'{reverse("account_login")}?next={url}'
        )

    @mock.patch('stripe.checkout.Session.create')
    def test_create_stripe_session_view_creates_user_learning_profile_if_none_exists(self, create_mock):

        # We're testing a side effect here, so we just need to prevent the stripe api
        # call from being made.
        temp_user = User.objects.create(
            username='u', 
            password='p',
            email='u@mail.com')
        self.client.force_login(temp_user)
        self.assertRaises(
            UserLearningProfile.DoesNotExist,
            UserLearningProfile.objects.get,
            user=temp_user,
        )
        sub_id = self.subscription.pk
        import stripe
        session = stripe.checkout.Session()
        session.url = '/'
        create_mock.return_value = session
        url = f'/video_lessons/create_checkout_session/{sub_id}'
        self.client.get(url)
        profile_set = UserLearningProfile.objects.filter(user=temp_user)
        self.assertEqual(len(profile_set), 1)


    def test_subscription_success_view_get_method_template_and_status_code(self):
        response = self.client.get('/video_lessons/subscription_success/')
        self.assertTemplateUsed('video_lessons/subscription_success.html')
        self.assertEqual(response.status_code, 200)

    def test_subscription_success_post_method_returns_404_for_anonymous_user(self):
        response = self.client.post('video_lessons/subscription_success/')
        self.assertEqual(response.status_code, 404)

    

    
