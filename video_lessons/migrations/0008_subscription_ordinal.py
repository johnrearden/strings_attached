# Generated by Django 4.1.5 on 2023-02-19 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_lessons', '0007_subscription_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='ordinal',
            field=models.IntegerField(default=1),
        ),
    ]