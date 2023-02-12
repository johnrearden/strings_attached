# Generated by Django 4.1.5 on 2023-02-12 13:36

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_specialoffer_reduced_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productassociation',
            name='weight',
            field=models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
