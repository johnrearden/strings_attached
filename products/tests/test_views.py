from django.test import TestCase
from products.views import ProductDisplay, ProductDetail, Category
from products.models import SpecialOffer, Product
from django.contrib.auth.models import User
from datetime import datetime, timedelta


class TestProductViews(TestCase):

    test_special_offer_price = 10
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

    def test_product_display_template_and_status_code(self):
        response = self.client.get('/products/')
        self.assertTemplateUsed(response, 'products/product_display.html')
        self.assertEqual(response.status_code, 200)

    def test_product_display_special_offers(self):
        response = self.client.get('/products/')
        self.assertIn(self.test_special_offer, response.context['special_offers'])
