# Generated by Django 3.2.16 on 2023-01-12 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_alter_product_audio_clip'),
    ]

    operations = [
        migrations.AddField(
            model_name='productassociation',
            name='weight',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='product',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=7),
        ),
    ]
