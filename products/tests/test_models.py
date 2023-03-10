from django.test import TestCase
from products.models import Product, Category, SpecialOffer, ProductAssociation
from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta


class TestProductsModels(TestCase):

    test_special_offer_price = 10
    test_standard_price = 20

    @classmethod
    def clean_it(cls, model):
        model.full_clean()

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
        cls.associated_product = Product.objects.create(
            name='Guitar2',
            category=cls.test_category,
            description='A cool guitar also.',
            price=cls.test_standard_price,
            stock_level=10,
            reorder_threshold=10,
            product_owner=cls.test_user)
        cls.test_special_offer = SpecialOffer.objects.create(
            product=cls.test_product,
            reduced_price=cls.test_special_offer_price,
            start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now() + timedelta(days=10),)

# Tests on Product model
    def test_product_str_method(self):
        self.assertIn(self.test_product.name, self.test_product.__str__())
        cat_name = self.test_product.category.name
        self.assertIn(cat_name, self.test_product.__str__())

    def test_email_sent_if_stock_low(self):
        self.test_product.stock_level = 0
        self.test_product.save()
        self.assertEqual(len(mail.outbox), 1)

    def test_product_creation_fails_with_negative_stock_levels(self):
        prod = Product.objects.create(
            name='Guitar',
            category=self.test_category,
            description='A cool guitar.',
            price=20.0,
            stock_level=-1,
            reorder_threshold=10,
            product_owner=self.test_user)
        self.assertRaises(ValidationError, lambda: self.clean_it(prod))

    def test_product_creation_fails_with_negative_reorder_threshold(self):
        prod = Product.objects.create(
            name='Guitar',
            category=self.test_category,
            description='A cool guitar.',
            price=20.0,
            stock_level=10,
            reorder_threshold=-10,
            product_owner=self.test_user)
        self.assertRaises(ValidationError, lambda: self.clean_it(prod))

    def test_product_creation_fails_with_negative_price(self):
        prod = Product.objects.create(
            name='Guitar',
            category=self.test_category,
            description='A cool guitar.',
            price=-20.0,
            stock_level=10,
            reorder_threshold=10,
            product_owner=self.test_user)
        self.assertRaises(ValidationError, lambda: self.clean_it(prod))

    def test_get_current_price_checks_for_special_offer(self):
        offer_price = self.test_product.get_current_price()
        self.assertEqual(offer_price, self.test_special_offer_price)

        # Change start date to after datetime.now() and test again.
        self.test_special_offer.start_date = datetime.now() + timedelta(days=1)
        self.test_special_offer.save()
        current_price = self.test_product.get_current_price()
        self.assertEqual(current_price, self.test_standard_price)

        # Change end date to before datetime.now() and test again.
        self.test_special_offer.start_date = datetime.now() - timedelta(days=2)
        self.test_special_offer.end_date = datetime.now() - timedelta(days=1)
        self.test_special_offer.save()
        current_price = self.test_product.get_current_price()
        self.assertEqual(current_price, self.test_standard_price)

# Tests on Category model
    def test_category_string_method(self):
        cat_name = self.test_category.name
        self.assertIn(cat_name, self.test_category.__str__())

# Tests on Special Offer model
    def test_special_offer_string_method(self):
        product = self.test_special_offer.product.name
        price = self.test_special_offer.reduced_price
        end = self.test_special_offer.end_date
        self.assertIn(product, self.test_special_offer.__str__())
        self.assertIn(str(price), self.test_special_offer.__str__())
        self.assertIn(str(end), self.test_special_offer.__str__())

    def test_creation_fails_with_negative_reduced_price(self):
        offer = SpecialOffer.objects.create(
            product=self.test_product,
            reduced_price=-1,
            start_date=datetime.now() - timedelta(days=1),
            end_date=datetime.now() + timedelta(days=1),
        )
        self.assertRaises(ValidationError, lambda: self.clean_it(offer))

    def test_special_offer_is_live_method(self):
        offer = SpecialOffer.objects.create(
            product=self.test_product,
            reduced_price=10,
            start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now() + timedelta(days=10),
        )
        self.assertTrue(offer.is_live())
        offer.start_date = datetime.now() + timedelta(days=5)
        offer.save()
        self.assertFalse(offer.is_live())
        offer.start_date = datetime.now() - timedelta(days=10)
        offer.end_date = datetime.now() - timedelta(days=5)
        offer.save()
        self.assertFalse(offer.is_live())

    def test_special_offer_start_date_after_end_date_raises_exception(self):
        offer = SpecialOffer.objects.create(
            product=self.test_product,
            reduced_price=10,
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(days=10),
        )
        self.assertRaises(ValidationError, lambda: self.clean_it(offer))

# Tests on ProductAssociation model
    def test_association_weight_less_than_1_raises_exception(self):
        association = ProductAssociation.objects.create(
            base_product=self.test_product,
            associated_product=self.associated_product,
            weight=-1,
        )
        self.assertRaises(ValidationError, lambda: self.clean_it(association))

    def test_product_association_with_same_product_raises_exception(self):
        association = ProductAssociation.objects.create(
            base_product=self.test_product,
            associated_product=self.test_product,
            weight=2,
        )
        self.assertRaises(ValidationError, lambda: self.clean_it(association))
    
    def test_product_association_string_method(self):
        association = ProductAssociation.objects.create(
            base_product=self.test_product,
            associated_product=self.associated_product,
        )
        name1 = association.base_product.name
        name2 = association.associated_product.name
        self.assertIn(name1, association.__str__())
        self.assertIn(name2, association.__str__())
