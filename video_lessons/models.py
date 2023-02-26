from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class LessonSeries(models.Model):
    """
    Represents a grouping of video lessons
    """
    name = models.CharField(max_length=64)
    description = models.TextField(max_length=1024, default='description...')

    def __str__(self):
        return self.name


class VideoLesson(models.Model):
    """
    Represents one video lesson, belonging to a series, with a 
        video file and an image file to show as a thumbnail for display. The
        ordinal field represents its place in the sequence of lessons. 
    """
    series = models.ForeignKey(LessonSeries, on_delete=models.CASCADE,
                               related_name='video_lessons')
    name = models.CharField(max_length=255)
    ordinal = models.IntegerField()
    video_file = models.FileField(upload_to='video_lessons/', max_length=255,
                                  null=True, blank=True)
    image = models.ImageField(upload_to='lesson_images/,', max_length=255,
                              null=True, blank=True)

    def __str__(self):
        return f'{self.name} from {self.series.name}'


class UserLearningProfile(models.Model):
    """
    Holds information about a user's subscribtion status. Includes flags for
    whether they are/have been a subscriber, and whether they are currently
    fully paid up. The expiration date is updated each time a payment is 
    received through the Stripe invoice.paid webhook. If the user is deleted,
    the profile remains, as it is possible that payments may still be being
    taken automatically by Stripe, and the ex-user may wish to recover their
    account.
    """
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True,
                                related_name='learning_profile')
    subscriber = models.BooleanField(default=False)
    subscription_paid = models.BooleanField(default=False)
    stripe_subscription_id = models.CharField(max_length=1024, null=True,
                                              blank=True)
    stripe_customer_id = models.CharField(max_length=1024, null=True,
                                          blank=True)
    subscription_expiration_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return (f'{self.user.username} (Subscriber:{self.subscriber})'
                f', paid up:{self.subscription_paid}')


class Subscription(models.Model):
    date_created = models.DateField(auto_now_add=True)
    name = models.CharField(max_length=256)
    description = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=6, decimal_places=2,
                                validators=[MinValueValidator(0),])
    image = models.ImageField(upload_to='subscription_images/', null=True,
                              blank=True)
    ordinal = models.IntegerField(default=1)
    stripe_lookup_id = models.CharField(max_length=255,
                                        default='no_key_assigned')

    def __str__(self):
        return f'Subscription : {self.name}'
