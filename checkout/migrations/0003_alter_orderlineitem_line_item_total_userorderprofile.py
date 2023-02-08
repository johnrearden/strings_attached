# Generated by Django 4.1.5 on 2023-02-08 19:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('checkout', '0002_order_payment_confirmed_order_pid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderlineitem',
            name='line_item_total',
            field=models.DecimalField(decimal_places=2, default=0, editable=False, max_digits=8),
        ),
        migrations.CreateModel(
            name='UserOrderProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=64)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=32)),
                ('country', models.CharField(max_length=64)),
                ('postcode', models.CharField(blank=True, max_length=32, null=True)),
                ('town_or_city', models.CharField(max_length=64)),
                ('street_address1', models.CharField(max_length=96)),
                ('street_address2', models.CharField(blank=True, max_length=96, null=True)),
                ('county', models.CharField(blank=True, max_length=32, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='order_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]