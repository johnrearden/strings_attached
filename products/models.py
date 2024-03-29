from django.db import models
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Category(models.Model):
    """ A category that contains products of a similar type """
    name = models.CharField(max_length=128)
    friendly_name = models.CharField(max_length=128)

    def __str__(self):
        return f'Category : {self.name}'


class SpecialOffer(models.Model):
    """ Represents a time-limited price reduction on a product."""

    def return_default_end_date():
        """ This method returns the datetime at the time of invocation
            plus 2 weeks """
        now = datetime.now()
        return now + timedelta(days=14)

    product = models.ForeignKey("products.Product", on_delete=models.CASCADE,
                                related_name='products')
    reduced_price = models.DecimalField(max_digits=6, decimal_places=2,
                                        validators=[MinValueValidator(0), ])
    start_date = models.DateField(default=datetime.now)
    end_date = models.DateField(default=return_default_end_date)

    def is_live(self):
        """ Returns true if the current date falls between the special offer
            start and end dates"""
        right_now = datetime.now()
        return self.start_date < right_now < self.end_date

    def __str__(self):
        return (f'Offer : {self.product} available at {self.reduced_price} '
                f'until {self.end_date}')

    def clean(self):
        """ Prevents a staff member inadvertently creating an invalid offer
            date range"""
        if self.start_date > self.end_date:
            raise ValidationError('Start date can\'t be after end date!')  


class Product(models.Model):
    """ A product purchaseable by the user """
    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    description = models.TextField()
    price = models.DecimalField(max_digits=7, decimal_places=2,
                                validators=[MinValueValidator(0)],)
    image = models.ImageField(upload_to='product_images/', null=True,
                              blank=True,
                              default='product_images/noimage.webp')
    audio_clip = models.FileField(upload_to='product_audio_clips/', null=True,
                                  blank=True)
    stock_level = models.IntegerField(default=0,
                                      validators=[MinValueValidator(0)],)
    reorder_threshold = models.IntegerField(default=5,
                                            validators=[MinValueValidator(0)],)
    product_owner = models.ForeignKey(User, on_delete=models.SET_NULL,
                                      related_name="owned_products",
                                      default=1, null=True)

    def __str__(self):
        return f'{self.name} (cat. {self.category.name})'

    def save(self, *args, **kwargs):
        """ Sends an email to the staff member designated as the product
            owner in the event that the stock level falls below the
            reorder threshold """
        if self.stock_level < self.reorder_threshold:
            send_mail(
                subject='Urgent! : Stock low',
                message=(f'Please reorder {self.name}\nStock is now down '
                         f'to {self.stock_level}'),
                from_email=None,
                recipient_list=[self.product_owner.email]
            )
        super(Product, self).save(*args, **kwargs)

    def get_current_price(self):
        """ Returns the price inclusive of the lowest currently valid
            special offer. """
        offers = SpecialOffer.objects.filter(product=self)
        now = datetime.now()
        current_offers = offers.filter(start_date__lte=now, end_date__gte=now)
        if current_offers:
            best_offer = current_offers.order_by('-reduced_price')[0]
            price = best_offer.reduced_price
        else:
            price = self.price
        return price


class ProductAssociation(models.Model):
    """
    A one-way link between one product and another, useful for recommending
    extra related purchases once user has chosen a product
    """
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                     related_name='from_product')
    associated_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='associated_products')

    # The weight field was originally intended to track products that were
    # bought together, possibly by incrementing the weight each time the
    # products were associated, but this was not in the end implemented in
    # the project.
    weight = models.IntegerField(default=1,
                                 validators=[MinValueValidator(1), ])

    def __str__(self):
        return (f'Association : from {self.base_product.name} to '
                f'{self.associated_product.name}')

    def clean(self):
        """ Prevents a product from being associated with itself """
        if self.base_product == self.associated_product:
            raise ValidationError('You can\'t associate a product with itself')
