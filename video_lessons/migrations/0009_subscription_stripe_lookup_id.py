# Generated by Django 4.1.5 on 2023-02-19 19:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_lessons', '0008_subscription_ordinal'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='stripe_lookup_id',
            field=models.CharField(default='no_key_assigned', max_length=255),
        ),
    ]
