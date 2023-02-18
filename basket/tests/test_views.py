from django.test import RequestFactory, TestCase
from django.contrib.auth.models import User
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from products.models import Category, Product, SpecialOffer
from checkout.models import UserOrderProfile
from datetime import datetime, timedelta


class TestViewBasketView(TestCase):

    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com',
            is_staff=True)
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
        cls.test_special_offer = SpecialOffer.objects.create(
            product=cls.test_product,
            reduced_price=4,
            start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now() + timedelta(days=10)
        )

    def test_view_basket_view_template_and_status_code(self):
        response = self.client.get('/basket/view_basket/')
        self.assertTemplateUsed('basket/basket.html')
        self.assertEqual(response.status_code, 200)

    def test_view_basket_context_contains_correct_item_and_quantity(self):
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        response = self.client.post(url, data=data)

        response = self.client.get('/basket/view_basket/')
        context_item = response.context['basket'][0]
        self.assertEqual(self.test_product, context_item['product'])
        self.assertEqual(1, context_item['quantity'])

    def test_view_basket_context_contains_special_offer(self):
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        response = self.client.post(url, data=data)

        # Check that special offer is in context.
        response = self.client.get('/basket/view_basket/')
        context_item = response.context['special_offers']
        self.assertEqual(self.test_special_offer, context_item[0])


class TestAddToBasketView(TestCase):

    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com',
            is_staff=True)
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

    def setUp(self):
        request = RequestFactory().get('/basket/view_basket')
        middleware = SessionMiddleware(request)
        middleware.process_request(request)
        request.session.save()

    def test_add_to_basket_view_redirects_to_url_in_post_request(self):
        data = {
            'redirect_url': '/',
            'quantity': 1}
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        response = self.client.post(url, data)
        self.assertRedirects(response=response, expected_url='/')

    def test_add_to_basket_view_places_item_in_basket(self):
        data = {
            'redirect_url': '/basket/view_basket',
            'quantity': 1,
        }
        url = f'/basket/add_to_basket/{self.test_product.id}'
        self.client.post(url, data)
        basket = self.client.session.get('basket', {})
        self.assertIn(str(self.test_product.id), list(basket.keys()))
        self.assertEqual(1, basket[str(self.test_product.id)])

    def test_add_to_basket_view_increases_quantity_for_existing_item(self):
        
        # Add one item to the basket
        data = {
            'redirect_url': '/',
            'quantity': 1}
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        self.client.post(url, data)

        # Add another 2 of the same item
        data = {
            'redirect_url': '/',
            'quantity': 3}
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        self.client.post(url, data)

        # Check that all 3 items are in the basket
        basket = self.client.session.get('basket', {})
        self.assertEqual(4, basket[str(self.test_product.id)])


class TestRemoveFromBasketView(TestCase):

    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com',
            is_staff=True)
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

    def test_remove_from_basket_view_removes_item(self):
        # Add an item to the basket
        data = {
            'redirect_url': '/',
            'quantity': 1}
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        self.client.post(url, data)

        # Remove the item from the basket.
        data = {'redirect_url': '/'}
        url = f'/basket/remove_from_basket/{self.test_product.id}'
        self.client.post(url, data)

        basket = self.client.session.get('basket', {})
        self.assertNotIn(str(self.test_product.id), list(basket.keys()))

    def test_remove_from_basket_view_redirects_to_url_in_post_request(self):
        data = {'redirect_url': '/'}
        url = f'/basket/remove_from_basket/{self.test_product.pk}'
        response = self.client.post(url, data)
        self.assertRedirects(response=response, expected_url='/')


class TestReplaceItemQuantityView(TestCase):
    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com',
            is_staff=True)
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
    
    def test_replace_item_quantity_view_alters_item_quantity(self):
        # Add an item to the basket
        data = {
            'redirect_url': '/',
            'quantity': 1}
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        self.client.post(url, data)

        # Try altering the quantity
        data = {
            'redirect_url': '/basket/view_basket/',
            'quantity': 3,
        }
        url = f'/basket/replace_item_quantity/{self.test_product.pk}'
        self.client.post(url, data)

        basket = self.client.session.get('basket', {})
        self.assertEqual(3, basket[str(self.test_product.pk)])

    def test_replace_item_quantity_view_redirects_to_url_in_post_request(self):
        data = {'redirect_url': '/', 'quantity': 3}
        url = f'/basket/replace_item_quantity/{self.test_product.pk}'
        response = self.client.post(url, data)
        self.assertRedirects(response=response, expected_url='/')


class TestEmptyBasketView(TestCase):
    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com',
            is_staff=True)
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

    def test_empty_basket_view_results_in_empty_basket(self):
        url = '/basket/empty_basket/'
        data = {}
        self.client.post(url, data)

        basket = self.client.session.get('basket', {})
        self.assertEqual(basket, {})
    
    def test_empty_basket_view_redirects_to_product_display_page(self):
        url = '/basket/empty_basket/'
        data = {}
        response = self.client.post(url, data)
        self.assertRedirects(response=response,
                             expected_url=reverse('product_display'))