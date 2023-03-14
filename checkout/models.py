import uuid
from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from products.models import Product


class Order(models.Model):
    """
    Models an order, including shipping details and other required fields
    for the Stripe checkout process. The order is saved on the system before
    the confirmPayment call is made to Stripe. There are boolean flags to
    indicate that the order payment has been confirmed, and whether or not
    the order has been fulfilled.
    """
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
    fulfilled = models.BooleanField(default=False, null=False)

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
        instrument_line_items = self.items \
            .filter(product__category__name='Instruments')
        if not instrument_line_items:
            self.delivery_cost = settings.DEFAULT_DELIVERY_CHARGE
        self.grand_total = self.order_total + self.delivery_cost
        self.grand_total -= self.discount
        self.save()

    def adjust_product_stock_levels(self):
        """ Update the stock levels of the line_item products after
            the order is fulfilled. Email product_owner if not enough
            stock is available to fulfill the order."""
        line_items = OrderLineItem.objects.filter(order=self)
        for item in line_items:
            prod = item.product
            prod.stock_level -= item.quantity
            if prod.stock_level < 0:
                # Stock level cannot be below 0. If the order can't be
                # fulfilled due to lack of stock, email the product owner.
                prod.stock_level = 0
                send_mail(
                    subject='Urgent! : Order unfulfilled, product o/o stock!',
                    message=(f'Please reorder {prod.name}\nThe following order'
                             f'cant currently be fulfilled : '
                             f'{self.order_number}\nThis order requires '
                             f'{item.quantity} x {prod.name}'),
                    from_email=None,
                    recipient_list=[prod.product_owner.email]
                )
            prod.save()

    def __str__(self):
        return f'Order {self.order_number} - total={self.grand_total}'


class OrderLineItem(models.Model):
    """
    Models an item (product and quantity) that appears in an order.
    """
    order = models.ForeignKey(Order, null=False, blank=False,
                              on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, null=False, blank=False,
                                on_delete=models.CASCADE)
    quantity = models.IntegerField(null=False, blank=False, default=0)
    line_item_total = models.DecimalField(max_digits=8, decimal_places=2,
                                          null=False, blank=False,
                                          editable=False, default=0)

    def save(self, *args, **kwargs):
        """ Set the line_item_total and update the order total """
        current_price = self.product.get_current_price()
        self.line_item_total = current_price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Product {self.product.name} : order {self.order.order_number}'


class UserOrderProfile(models.Model):
    """
    Models a user's order information, so that it can be reused in
    subsequent purchases (with the user's opt-in consent)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='order_profile')
    full_name = models.CharField(max_length=64)
    email = models.EmailField(max_length=254)
    phone_number = models.CharField(max_length=32)
    country = models.CharField(max_length=64)
    postcode = models.CharField(max_length=32, null=True, blank=True)
    town_or_city = models.CharField(max_length=64)
    street_address1 = models.CharField(max_length=96)
    street_address2 = models.CharField(max_length=96, null=True, blank=True)
    county = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name} ({self.email})'
