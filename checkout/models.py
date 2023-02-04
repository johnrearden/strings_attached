import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=32, editable=False)
    full_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=32)
    country = models.CharField(max_length=64)
    postcode = models.CharField(max_length=32, null=True, blank=True)
    town_or_city = models.CharField(max_length=64)
    street_address1 = models.CharField(max_length=96)
    street_address2 = models.CharField(max_length=96, null=True, blank=True)
    county = models.CharField(max_length=32, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_cost = models.DecimalField(max_digits=8, decimal_places=2,
                                        null=False, default=0)
    discount = models.DecimalField(max_digits=3, decimal_places=2,
                                   null=False, default=0)                                        
    order_total = models.DecimalField(max_digits=8, decimal_places=2,
                                      null=False, default=0)
    grand_total = models.DecimalField(max_digits=8, decimal_places=2,
                                      null=False, default=0)
    pid = models.CharField(max_length=256, editable=False, default='None')
    payment_confirmed = models.BooleanField(default=False, null=False)

    def _create_order_number(self):
        """ Create a random, unique order number using UUID """
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """ If this order doesn't yet have an order number, generate one
            before saving it """
        if not self.order_number:
            self.order_number = self._create_order_number()
        super().save(*args, **kwargs)

    def update_total(self):
        """ Update overall total each time an order line item is added
            to the order """
        sum = Sum('line_item_total')
        self.order_total = self.items.aggregate(sum)['line_item_total__sum']

        # Check for delivery charge on orders not including an instrument
        instrument_line_items = self.items.filter(category__name='Instrument')
        if not instrument_line_items:
            self.delivery_cost = settings.DEFAULT_DELIVERY_CHARGE
        self.grand_total = self.order_total + self.delivery_cost
        self.grand_total -= self.discount
        self.save()

    def __str__(self):
        return f'Order {self.order_number} - total={self.grand_total}'


class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, null=False, blank=False,
                              on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, null=False, blank=False,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    line_item_total = models.DecimalField(max_digits=8, decimal_places=2,
                                          null=False, blank=False,
                                          editable=False)

    def save(self, *args, **kwargs):
        """ Set the line_item_total and update the order total """
        self.line_item_total = self.product.price * self.quantity
        super.save(*args, **kwargs)

    def __str__(self):
        return f'Product {self.product.name} : order {self.order.order_number}'
