# Generated by Django 4.1.5 on 2023-03-26 17:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_remove_product_audio_url_remove_product_image_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialoffer',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2023, 4, 9, 17, 29, 53, 411470)),
        ),
        migrations.AlterField(
            model_name='specialoffer',
            name='start_date',
            field=models.DateField(default=datetime.datetime(2023, 3, 26, 17, 29, 53, 411462)),
        ),
    ]
