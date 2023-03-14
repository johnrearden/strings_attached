from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from django.core import mail
from checkout.models import Order, OrderLineItem, UserOrderProfile
from products.models import Category, Product


class TestOrderModel(TestCase):
    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com')
        cls.test_category = Category.objects.create(
            name='Instruments',
            friendly_name='Instruments')
        cls.test_product = Product.objects.create(
            name='Guitar',
            category=cls.test_category,
            description='A cool guitar.',
            price=cls.test_standard_price,
            stock_level=10,
            reorder_threshold=10,
            product_owner=cls.test_user)
        cls.test_order = Order.objects.create(
            full_name='name',
            email='name@name.com',
            phone_number='08123456789',
            country='transylvania',
            postcode='A234P234',
            town_or_city='town',
            street_address1='street',
            street_address2='street2',
            county='county',
        )
        cls.test_order_line_item = OrderLineItem.objects.create(
            order=cls.test_order,
            product=cls.test_product,
            quantity=1,
        )

    def test_order_model_string_method(self):
        self.assertIn(self.test_order.order_number, self.test_order.__str__())

    def test_order_number_automatically_generated(self):
        # Class test order is created without order number specified.
        self.assertTrue(self.test_order.order_number is not None)

    def test_update_total_method(self):
        has_instrument = False
        total = 0
        line_items = OrderLineItem.objects.filter(order=self.test_order)
        for item in line_items:
            if item.product.category.name == 'Instruments':
                has_instrument = True
            total += item.product.get_current_price()
        if not has_instrument:
            total -= settings.DEFAULT_DELIVERY_CHARGE

        self.test_order.update_total()
        self.assertEqual(total, self.test_order.grand_total)

    def test_adjust_product_stock_levels_correctly_reduces_stock_level(self):
        initial_stock_level = 10
        temp_prod = Product.objects.create(
            name='Guitartemp',
            category=self.test_category,
            description='A cool guitar.',
            price=self.test_standard_price,
            stock_level=initial_stock_level,
            reorder_threshold=10,
            product_owner=self.test_user)
        temp_order = Order.objects.create(
            full_name='name',
            email='name@name.com',
            phone_number='08123456789',
            country='transylvania',
            postcode='A234P234',
            town_or_city='town',
            street_address1='street',
            street_address2='street2',
            county='county',
        )
        OrderLineItem.objects.create(
            order=temp_order,
            product=temp_prod,
            quantity=1,
        )
        temp_order.adjust_product_stock_levels()
        # Fetch the updated instance from the db
        temp_prod = Product.objects.get(pk=temp_prod.pk)
        self.assertEqual(temp_prod.stock_level, initial_stock_level - 1)

    def test_adjust_product_stock_levels_sends_email_if_level_lte_0(self):
        initial_stock_level = 1
        temp_prod = Product.objects.create(
            name='Guitartemp',
            category=self.test_category,
            description='A cool guitar.',
            price=self.test_standard_price,
            stock_level=initial_stock_level,
            reorder_threshold=10,
            product_owner=self.test_user)
        temp_order = Order.objects.create(
            full_name='name',
            email='name@name.com',
            phone_number='08123456789',
            country='transylvania',
            postcode='A234P234',
            town_or_city='town',
            street_address1='street',
            street_address2='street2',
            county='county',
        )
        OrderLineItem.objects.create(
            order=temp_order,
            product=temp_prod,
            quantity=2,
        )
        temp_order.adjust_product_stock_levels()
        # Fetch the updated instance from the db
        temp_prod = Product.objects.get(pk=temp_prod.pk)
        self.assertEqual(temp_prod.stock_level, 0)

        # There should be 3 emails in the outbox. 1 for the unfulfilled order
        # warning, 2 for the stock low warning (prod.save() is called twice)
        warning_email_sent = False
        for sent_mail in mail.outbox:
            if 'Order unfulfilled'.upper() in sent_mail.subject.upper():
                warning_email_sent = True
        self.assertTrue(warning_email_sent)


class TestOrderLineItem(TestCase):
    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com')
        cls.test_category = Category.objects.create(
            name='Instruments',
            friendly_name='Instruments')
        cls.test_product = Product.objects.create(
            name='Guitar',
            category=cls.test_category,
            description='A cool guitar.',
            price=cls.test_standard_price,
            stock_level=10,
            reorder_threshold=10,
            product_owner=cls.test_user)
        cls.test_order = Order.objects.create(
            full_name='name',
            email='name@name.com',
            phone_number='08123456789',
            country='transylvania',
            postcode='A234P234',
            town_or_city='town',
            street_address1='street',
            street_address2='street2',
            county='county',
        )
        cls.test_order_line_item = OrderLineItem.objects.create(
            order=cls.test_order,
            product=cls.test_product,
            quantity=1,
        )

    def test_order_line_item_string_method(self):
        self.assertIn(self.test_order_line_item.product.name,
                      self.test_order_line_item.__str__())
        self.assertIn(self.test_order_line_item.order.order_number,
                      self.test_order_line_item.__str__())

    def test_order_line_item_save_method_calculates_price_correctly(self):
        # No price was specified in the test_order_line_item creation above.
        # It should be present
        price = self.test_order_line_item.product.get_current_price() * \
            self.test_order_line_item.quantity
        self.assertEqual(price, self.test_order_line_item.line_item_total)


class TestUserOrderProfile(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com')
        cls.test_user_profile = UserOrderProfile.objects.create(
            user=cls.test_user,
            full_name='name',
            email='name@name.com',
            phone_number='08123456789',
            country='transylvania',
            postcode='A234P234',
            town_or_city='town',
            street_address1='street',
            street_address2='street2',
            county='county',
        )

    def test_user_order_profile_string_method(self):
        self.assertIn(self.test_user_profile.full_name,
                      self.test_user_profile.__str__())
        self.assertIn(self.test_user_profile.email,
                      self.test_user_profile.__str__())
