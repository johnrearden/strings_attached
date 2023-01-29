from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.core.mail import send_mail


class Category(models.Model):
    """ A category that contains products of a similar type """
    name = models.CharField(max_length=128)
    friendly_name = models.CharField(max_length=128)

    def __str__(self):
        return f'Category : {self.name}'


class Product(models.Model):
    """ A product purchaseable by the user """
    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True,
                              blank=True)
    audio_url = models.URLField(max_length=1024, null=True, blank=True)
    audio_clip = models.FileField(upload_to='product_audio_clips', null=True,
                                  blank=True)
    stock_level = models.IntegerField(default=20)
    reorder_threshold = models.IntegerField(default=5)
    product_owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                                      related_name="owned_products",
                                      default=1, null=True)

    def __str__(self):
        return f'{self.name} (cat. {self.category.name})'

    def save(self, *args, **kwargs):
        if self.stock_level < self.reorder_threshold:
            send_mail(
                subject='Urgent! : Stock low',
                message=(f'Please reorder {self.name}\nStock is now down '
                         f'to {self.stock_level}'),
                from_email=None,
                recipient_list=[self.product_owner.email]
            )
        super(Product, self).save(*args, **kwargs)


class ProductAssociation(models.Model):
    """
    A one-way link between one product and another, useful for recommending
    extra related purchases once user has chosen a product
    """
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                     related_name='from_product')
    associated_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='associated_products')
    weight = models.IntegerField(default=1)

    def __str__(self):
        return (f'Association : from {self.base_product.name} to '
                f'{self.associated_product.name}')


class SpecialOffer(models.Model):
    """ Represents a time-limited price reduction on a product. In some
        cases, a second product is required """
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='products')
    reduced_price = models.DecimalField(max_digits=6, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def is_live(self):
        now = datetime.now()
        return self.start_date < now < self.end_date

    def __str__(self):
        return (f'Offer : {self.product} available at {self.reduced_price} '
                f'until {self.end_date}')
