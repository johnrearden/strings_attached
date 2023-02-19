from django.db import models
from django.contrib.auth.models import User


class LessonSeries(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=1024, default='description...')

    def __str__(self):
        return self.name


class VideoLesson(models.Model):
    series = models.ForeignKey(LessonSeries, on_delete=models.CASCADE,
                               related_name='video_lessons')
    name = models.CharField(max_length=255)
    ordinal = models.IntegerField()
    video_file = models.FileField(upload_to='video_lessons/', max_length=255)
    image = models.ImageField(upload_to='lesson_images/,', max_length=255)

    def __str__(self):
        return f'{self.name} from {self.series.name}'


class UserLearningProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='learning_profile')
    subscriber = models.BooleanField(default=False)
    subscription_paid = models.BooleanField(default=False)

    def __str__(self):
        return (f'{self.user.username} (Subscriber:{self.subscriber})'
                f', paid up:{self.subscription_paid}')


class Subscription(models.Model):
    date_created = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='subscription_images/', null=True,
                              blank=True)
    ordinal = models.IntegerField(default=1)
    stripe_lookup_id = models.CharField(max_length=255,
                                        default='no_key_assigned')

    def __str__(self):
        return f'Subscription : {self.name}'
