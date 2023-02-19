from django.contrib import admin
from .models import LessonSeries, VideoLesson, UserLearningProfile, \
                    Subscription


class LessonSeriesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description',)
    list_editable = ('name', 'description',)


class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'series', 'video_file', 'image',)
    list_editable = ('name', 'series', 'video_file', 'image',)


class UserLearningProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subscriber', 'subscription_paid',)
    list_editable = ('user', 'subscriber', 'subscription_paid',)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image', 'ordinal',
                    'date_created', 'price', 'stripe_lookup_id')
    list_editable = ('name', 'description', 'image', 'ordinal', 'price',
                     'stripe_lookup_id')


admin.site.register(LessonSeries, LessonSeriesAdmin)
admin.site.register(VideoLesson, VideoLessonAdmin)
admin.site.register(UserLearningProfile, UserLearningProfileAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
