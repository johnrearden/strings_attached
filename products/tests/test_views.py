from django.test import TestCase
from products.views import ProductDisplay, ProductDetail, Category, ProductAssociation
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
        cls.test_association = ProductAssociation.objects.create(
            base_product=cls.test_product,
            associated_product=cls.associated_product
        )

    def test_product_display_template_and_status_code(self):
        response = self.client.get('/products/')
        self.assertTemplateUsed(response, 'products/product_display.html')
        self.assertEqual(response.status_code, 200)

    def test_product_display_special_offers_returned_in_response(self):
        response = self.client.get('/products/')
        self.assertIn(self.test_special_offer,
                      response.context['special_offers'])
        self.assertEqual(len(response.context['special_offers']), 1)

    def test_product_filtering_by_category(self):
        # Test all products request
        response = self.client.get('/products/?category=all')
        products = response.context['products']
        all_product_db_count = len(Product.objects.all())
        self.assertEqual(len(products), all_product_db_count)

        # Test individual category requests
        for category in Category.objects.all():
            response = self.client.get(f'/products/?category={category.name}')
            products = response.context['products']
            category_product_db_count = len(
                Product.objects.filter(category=category))
            self.assertEqual(len(products), category_product_db_count)
            for product in products:
                self.assertEqual(product.category, category)

    def test_product_filtering_by_search_term(self):
        search_term_that_exists = 'guitar'
        search_term_that_doesnt_exist = '58y8usbNiLItE57GwbEm'
        search_term_in_one_description_only = 'also'
        products = Product.objects.all()

        # Filter the results using Python after fetching them from db,
        # to also test the Django filtering logic in the view.
        term = search_term_that_exists
        response = self.client.get(f'/products/?search={term}')
        filtered = list(filter(lambda p: term in p.name or term in p.description, products))
        self.assertEqual(list(response.context['products']), filtered)

        # Check a random 20-digit string to ensure no product is returned
        term = search_term_that_doesnt_exist
        response = self.client.get(f'/products/?search={term}')
        filtered = list(filter(lambda p: term in p.name or term in p.description, products))
        self.assertEqual(len(response.context['products']), 0)

        # Check a search term that appears only in one of the product descriptions
        term = search_term_in_one_description_only
        response = self.client.get(f'/products/?search={term}')
        filtered = list(filter(lambda p: term in p.name or term in p.description, products))
        self.assertEqual(len(response.context['products']), 1)

    def test_product_detail_view_template_and_status_code_correct(self):
        response = self.client.get(f'/products/{self.test_product.id}')
        self.assertTemplateUsed('/products/product_detail.html')
        self.assertEqual(response.status_code, 301)

    def test_product_detail_view_includes_associated_product(self):
        response = self.client.get(f'/products/{self.test_product.id}/')
        self.assertIn(self.associated_product, response.context['associated_products'])

    def test_product_detail_view_includes_special_offers(self):
        response = self.client.get(f'/products/{self.test_product.id}/')
        self.assertEqual(self.test_special_offer, response.context['offer'])

    def test_product_detail_view_includes_price_reduction(self):
        response = self.client.get(f'/products/{self.test_product.id}/')
        correct_reduction = self.test_product.price - self.test_special_offer.reduced_price
        self.assertEqual(correct_reduction, response.context['reduction'])
