from django.test import TestCase
from django.contrib.auth.models import User
from products.models import Product, Category, SpecialOffer
from datetime import datetime, timedelta


class TestProductAddView(TestCase):

    def test_product_add_view_template(self):
        self.client.get('/stock/add_product/')
        self.assertTemplateUsed('/stock/product_add_form.html')

    def test_product_add_view_redirects_with_user_logged_out(self):
        response = self.client.get('/stock/add_product/', follow=True)
        self.assertIn('accounts/login', str(response.redirect_chain[0]))

    def test_product_add_view_with_user_logged_in(self):
        test_user = User.objects.create(
            username='test',
            password='pass',
            is_staff=True
        )
        self.client.force_login(test_user, backend=None)
        response = self.client.get('/stock/add_product/')
        self.assertTemplateUsed('/stock/product_add_form.html')
        self.assertEqual(response.status_code, 200)


class TestProductUpdateView(TestCase):

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

    def test_product_update_view_template(self):
        self.client.get(f'/stock/update_product/{self.test_product.pk}')
        self.assertTemplateUsed('/stock/product_update_form.html')

    def test_product_update_view_redirects_with_user_logged_out(self):
        response = self.client.get(f'/stock/update_product/{self.test_product.pk}', follow=True)
        self.assertIn('accounts/login', str(response.redirect_chain[0]))

    def test_product_update_view_with_user_logged_in(self):
        self.client.force_login(self.test_user, backend=None)
        response = self.client.get(f'/stock/update_product/{self.test_product.pk}')
        self.assertTemplateUsed('/stock/product_update_form.html')
        self.assertEqual(response.status_code, 200)


class TestStaffProductList(TestCase):
    test_standard_price = 20
    test_special_offer_price = 10

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
        cls.test_special_offer = SpecialOffer.objects.create(
            product=cls.test_product,
            reduced_price=cls.test_special_offer_price,
            start_date=datetime.now() - timedelta(days=10),
            end_date=datetime.now() + timedelta(days=10),)

    def test_staff_product_list_template(self):
        self.client.get('/stock/staff_product_list/no_key')
        self.assertTemplateUsed('/stock/staff_product_list.html')

    def test_staff_product_list_redirects_with_user_logged_out(self):
        response = self.client.get('/stock/staff_product_list/no_key', follow=True)
        self.assertIn('accounts/login', str(response.redirect_chain[0]))

    def test_staff_product_list_with_user_logged_in(self):
        self.client.force_login(self.test_user, backend=None)
        response = self.client.get('/stock/staff_product_list/no_key')
        self.assertTemplateUsed('/stock/staff_product_list.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_product_list_includes_special_offers(self):
        self.client.force_login(self.test_user, backend=None)
        response = self.client.get('/stock/staff_product_list/all')
        self.assertTrue(response.context['products'][0]['on_special'])

    def test_staff_product_list_sorts_correctly_by_price(self):
        Product.objects.create(
            name='Guitar2',
            category=self.test_category,
            description='A cool guitar also.',
            price=30,
            stock_level=10,
            reorder_threshold=10,
            product_owner=self.test_user)
        self.client.force_login(self.test_user, backend=None)

        # Check with sort key 'price'
        response = self.client.get('/stock/staff_product_list/price')
        products = response.context['products']
        sorted_list = sorted(products, key=lambda p: p['price'])
        self.assertEqual(products, sorted_list)

        # Also check with sort key '-price' for reversed list
        response = self.client.get('/stock/staff_product_list/-price')
        products = response.context['products']
        sorted_list = sorted(products, key=lambda p: p['price'], reverse=True)
        self.assertEqual(products, sorted_list)

    def test_staff_product_list_flags_stock_low_on_product(self):
        test_low_stock_prod = Product.objects.create(
            name='Guitar2',
            category=self.test_category,
            description='A cool guitar also.',
            price=30,
            stock_level=5,
            reorder_threshold=10,
            product_owner=self.test_user)
        self.client.force_login(self.test_user, backend=None)
        response = self.client.get('/stock/staff_product_list/stock-low')
        products = response.context['products']
        low_stock_prods = list(filter(lambda p: p['name'] == test_low_stock_prod.name, products))
        test_low_stock_prod = low_stock_prods[0]
        self.assertTrue(test_low_stock_prod['stock_low'])

    def test_staff_product_list_sorts_correctly_by_category(self):
        self.client.force_login(self.test_user, backend=None)
        response = self.client.get('/stock/staff_product_list/category')
        products = response.context['products']
        sorted_list = sorted(products, key=lambda p: p['category'])
        self.assertEqual(products, sorted_list)

        # Check reverse order also
        response = self.client.get('/stock/staff_product_list/-category')
        products = response.context['products']
        sorted_list = sorted(products, key=lambda p: p['category'], reverse=True)
        self.assertEqual(products, sorted_list)


