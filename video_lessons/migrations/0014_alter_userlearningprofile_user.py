# Generated by Django 4.1.5 on 2023-02-26 09:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('video_lessons', '0013_alter_videolesson_image_alter_videolesson_video_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlearningprofile',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='learning_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
