from django.test import TestCase
from django.contrib.auth.models import User
from video_lessons.models import VideoLesson, UserLearningProfile,\
    LessonSeries, Subscription
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class TestVideoLessonModels(TestCase):

    @classmethod
    def clean_it(cls, model):
        model.full_clean()

    @classmethod
    def setUpTestData(cls):
        cls.lesson_series = LessonSeries.objects.create(
            name='test_lesson_series')
        cls.video_lesson = VideoLesson.objects.create(
            series=cls.lesson_series,
            name='test_video',
            ordinal=1,
        )
        cls.user = User.objects.create(
            username='test',
            password='password',
            email='testemail@mail.com',)
        cls.profile = UserLearningProfile.objects.create(
            user=cls.user,
        )
        cls.subscription = Subscription.objects.create(
            name='test_sub',
            price=20,
            description='description',
        )

    def test_lesson_series_string_method_returns_name(self):
        self.assertIn(self.lesson_series.name, self.lesson_series.__str__())

    def test_video_lesson_str_method_contains_name_and_series(self):
        self.assertIn(self.video_lesson.name, self.video_lesson.__str__())
        self.assertIn(self.video_lesson.series.name, self.video_lesson.__str__())

    def test_user_learning_profile_str_method_includes_username_and_flags(self):
        self.assertIn(self.user.username, self.profile.__str__())

    def test_user_learning_profile_remains_if_user_is_deleted(self):
        temp_user = User.objects.create(
            username='temp', password='pass'
        )
        learning_profile = UserLearningProfile.objects.create(
            user=temp_user,
        )
        id = learning_profile.pk
        temp_user.delete()
        self.assertIn(learning_profile, UserLearningProfile.objects.filter(pk=id))

    def test_subscription_str_method_contains_name(self):
        self.assertIn(self.subscription.name, self.subscription.__str__())

    def test_subscription_ordinal_defaults_to_1(self):
        temp_sub = Subscription.objects.create(
            name='test_sub',
            price=20,
            description='descriptio'
        )
        self.assertEqual(temp_sub.ordinal, 1)

    def test_subscription_price_cannot_be_negative(self):
        temp_sub = Subscription.objects.create(
            name='test_sub',
            price=-20,
            description='descriptio'
        )
        self.assertRaises(ValidationError, lambda: self.clean_it(temp_sub))
