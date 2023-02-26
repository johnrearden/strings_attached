from django.test import TestCase
from django.contrib.auth.models import User
from video_lessons.views import *


class TestVideoLessonViews(TestCase):
    def test_all_lessons_view_template_and_status_code(self):
        pass

    def test_all_lessons_view_grants_full_access_to_paid_up_subscriber(self):
        pass

    def test_all_lessons_view_doesnt_grant_full_access_to_anonymous_user(self):
        pass

    def test_no_full_access_for_subscriber_not_paid_up(self):
        pass

    def test_all_lessons_view_returns_all_available_series_and_their_lessons(self):
        pass

    def test_video_player_template_and_status_code(self):
        pass

    def test_video_player_grants_full_access_to_paid_up_subscriber(self):
        pass

    def test_subscription_options_view_template_and_status_code(self):
        pass

    def test_anonymous_user_cant_access_create_stripe_checkout_session_view(self):
        pass

    def test_create_stripe_session_view_creates_user_learning_profile_if_none_exists(self):
        pass

    def test_subscription_success_view_get_method_template_and_status_code(self):
        pass

    def test_subscription_cancelled_view_template_and_status_code(self):
        pass