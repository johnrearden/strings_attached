from django.db import models


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
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(upload_to='product_images/', null=True,
                              blank=True)
    audio_url = models.URLField(max_length=1024, null=True, blank=True)
    audio_clip = models.FileField(upload_to='product_audio_clips', null=True,
                                  blank=True)

    def __str__(self):
        return f'{self.name} (cat. {self.category.name})'


class ProductAssociation(models.Model):
    """
    A one-way link between one product and another, useful for recommending
    extra related purchases once user has chosen a product
    """
    base_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                     related_name='from_product')
    associated_product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                           related_name='associated_products')

    def __str__(self):
        return (f'Association : from {self.base_product.name} to '
                f'{self.associated_product.name}')


class SpecialOffer(models.Model):
    """ Represents a time-limited price reduction on a product """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    reduced_price = models.DecimalField(max_digits=6, decimal_places=2)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return (f'Offer : {self.product} available at {self.reduced_price} '
                f'until {self.end_date}')
