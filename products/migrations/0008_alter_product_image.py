# Generated by Django 4.1.5 on 2023-03-15 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_product_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='product_images/noimage.png', null=True, upload_to='product_images/'),
        ),
    ]
