from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from products.models import Category, Product
from checkout.models import UserOrderProfile, Order, OrderLineItem


class TestCheckoutView(TestCase):
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

    def test_checkout_view_template_and_status_code(self):
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        response = self.client.post(url, data=data)
        
        response = self.client.get('/checkout/')
        self.assertTemplateUsed('checkout/checkout.html')
        self.assertEqual(response.status_code, 200)

    def test_checkout_view_redirects_if_basket_empty(self):
        response = self.client.get('/checkout/', follow=True)
        self.assertRedirects(response=response, expected_url='/products/')

    def test_checkout_form_empty_if_user_profile_does_not_exist(self):
        no_profile_user = User.objects.create(
            username='no_profile',
            password='tinfoil_hat'
        )

        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        response = self.client.post(url, data=data)

        self.client.force_login(no_profile_user, backend=None)
        response = self.client.get('/checkout/')
        self.assertNotIn('value="', response.context['order_form'])

    def test_checkout_form_populated_if_user_order_profile_exists(self):
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        response = self.client.post(url, data=data)

        self.client.force_login(self.test_user, backend=None)
        response = self.client.get('/checkout/')
        profile = self.test_user_profile
        form = response.context['order_form']
        self.assertEqual(profile.full_name, form['full_name'].value())
        self.assertEqual(profile.email, form['email'].value())
        self.assertEqual(profile.phone_number, form['phone_number'].value())
        self.assertEqual(profile.country, form['country'].value())
        self.assertEqual(profile.postcode, form['postcode'].value())
        self.assertEqual(profile.town_or_city, form['town_or_city'].value())
        self.assertEqual(profile.street_address1, form['street_address1'].value())
        self.assertEqual(profile.street_address2, form['street_address2'].value())
        self.assertEqual(profile.county, form['county'].value())


class TestSaveOrderView(TestCase):
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
        
    def test_save_order_view_returns_200(self):
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        response = self.client.post(url, data=data)

        # Create a mock post from the front-end.
        data = {
            'csrfmiddlewaretoken': ['7bHIabjDJfTEuYsJM8lzY2flKWYyjuRPFEkC1kXEu2SbPnT80Q61c9tF4wP370UA'],
            'full_name': ['name'],
            'email': ['name@mail.com'],
            'phone_number': ['123456789'],
            'street_address1': ['add1'],
            'street_address2': ['add2'],
            'town_or_city': ['town'],
            'county': ['county'],
            'postcode': ['code'],
            'country': ['country'],
            'client_secret': ['pi_3MbmXFHM4JtBDaOL1LvZDSXQ_secret_YoVTWqbfBRp3kW20QmtZmSNKJ']
        }

        response = self.client.post('/checkout/save_order/', data)
        self.assertEqual(response.status_code, 200)

    def test_save_order_view_saves_order_in_db(self):
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        self.client.post(url, data=data)

        # Create a mock post from the front-end.
        test_client_secret = 'pi_3MbmXFHM4JtBDaOL1LvZDSXQ_secret_YoVTWqbfBRp3kW20QmtZmSNKJ'
        data = {
            'csrfmiddlewaretoken': ['7bHIabjDJfTEuYsJM8lzY2flKWYyjuRPFEkC1kXEu2SbPnT80Q61c9tF4wP370UA'],
            'full_name': ['name'],
            'email': ['name@mail.com'],
            'phone_number': ['123456789'],
            'street_address1': ['add1'],
            'street_address2': ['add2'],
            'town_or_city': ['town'],
            'county': ['county'],
            'postcode': ['code'],
            'country': ['country'],
            'client_secret': [test_client_secret]
        }
        self.client.post('/checkout/save_order/', data)

        # Try to retrieve the order from the database, testing all fields.
        pid = test_client_secret.split('_secret')[0]
        self.assertEqual(len(Order.objects.filter(
            pid=pid,
            full_name='name',
            email='name@mail.com',
            phone_number='123456789',
            street_address1='add1',
            street_address2='add2',
            town_or_city='town',
            county='county',
            postcode='code',
            country='country',
        )), 1)

    def test_save_order_view_saves_profile_if_not_already_exists(self):
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        self.client.post(url, data=data)

        # Create a mock post from the front-end.
        test_client_secret = 'pi_3MbmXFHM4JtBDaOL1LvZDSXQ_secret_YoVTWqbfBRp3kW20QmtZmSNKJ'
        data = {
            'csrfmiddlewaretoken': ['7bHIabjDJfTEuYsJM8lzY2flKWYyjuRPFEkC1kXEu2SbPnT80Q61c9tF4wP370UA'],
            'full_name': ['name'],
            'email': ['name@mail.com'],
            'phone_number': ['123456789'],
            'street_address1': ['add1'],
            'street_address2': ['add2'],
            'town_or_city': ['town'],
            'county': ['county'],
            'postcode': ['code'],
            'country': ['country'],
            'save-info': ['on'],
            'client_secret': [test_client_secret]
        }

        # Login the test_user, check no profile exist and post to the view
        self.client.force_login(self.test_user, backend=None)
        profiles = UserOrderProfile.objects.filter(user=self.test_user)
        self.assertEqual(len(profiles), 0)
        self.client.post('/checkout/save_order/', data)

        profiles = UserOrderProfile.objects.filter(user=self.test_user)
        self.assertEqual(len(profiles), 1)

    def test_save_order_view_modifies_profile_if_already_exists(self):

        profile_new_name = 'new_name'

        # Create an existing User_Order_Profile in the database
        UserOrderProfile.objects.create(
            user=self.test_user,
            full_name='name',
            email='name@email.com',
            phone_number=232323,
            country='country',
            town_or_city='town',
            street_address1='add1',
        )

        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        self.client.post(url, data=data)

        # Create a mock post from the front-end.
        test_client_secret = 'pi_3MbmXFHM4JtBDaOL1LvZDSXQ_secret_YoVTWqbfBRp3kW20QmtZmSNKJ'
        data = {
            'csrfmiddlewaretoken': ['7bHIabjDJfTEuYsJM8lzY2flKWYyjuRPFEkC1kXEu2SbPnT80Q61c9tF4wP370UA'],
            'full_name': [profile_new_name],  # name has changed to 'new_name'
            'email': ['name@mail.com'],
            'phone_number': ['123456789'],
            'street_address1': ['add1'],
            'street_address2': ['add2'],
            'town_or_city': ['town'],
            'county': ['county'],
            'postcode': ['code'],
            'country': ['country'],
            'save-info': ['on'],
            'client_secret': [test_client_secret]
        }

        # Login the test_user and post the data to the view
        self.client.force_login(self.test_user, backend=None)
        self.client.post('/checkout/save_order/', data)

        # Check that the name
        profiles = UserOrderProfile.objects.filter(user=self.test_user)
        self.assertEqual(len(profiles), 1)
        profile = profiles[0]
        self.assertEqual(profile.full_name, profile_new_name)


class TestPaymentConfirmedView(TestCase):

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
            reorder_threshold=5,
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
        # Put a test item in the basket
        url = f'/basket/add_to_basket/{self.test_product.pk}'
        data = {'quantity': 1, 'redirect_url': '/'}
        self.client.post(url, data=data)

        # Create a mock post from the front-end.
        test_client_secret = 'pi_3MbmXFHM4JtBDaOL1LvZDSXQ_secret_YoVTWqbfBRp3kW20QmtZmSNKJ'
        data = {
            'csrfmiddlewaretoken': ['7bHIabjDJfTEuYsJM8lzY2flKWYyjuRPFEkC1kXEu2SbPnT80Q61c9tF4wP370UA'],
            'full_name': ['name'],
            'email': ['name@mail.com'],
            'phone_number': ['123456789'],
            'street_address1': ['add1'],
            'street_address2': ['add2'],
            'town_or_city': ['town'],
            'county': ['county'],
            'postcode': ['code'],
            'country': ['country'],
            'client_secret': [test_client_secret]
        }

        # Post the data to the save_order view
        self.client.post('/checkout/save_order/', data)

    def test_payment_confirmed_view_sets_confirmed_flag_on_order(self):

        # Create a mock post from the front-end.
        test_client_secret = 'pi_3MbmXFHM4JtBDaOL1LvZDSXQ_secret_YoVTWqbfBRp3kW20QmtZmSNKJ'
        data = {
            'payment_confirmed': 'True',
            'client_secret': [test_client_secret],
        }
        response = self.client.post('/checkout/payment_confirmed/', data)
        pid = data.get('client_secret')[0].split('_secret')[0]
        order = Order.objects.get(pid=pid)
        self.assertTrue(order.payment_confirmed)

    def test_payment_confirmed_view_sends_email_to_customer(self):

        # Create a mock post from the front-end.
        test_client_secret = 'pi_3MbmXFHM4JtBDaOL1LvZDSXQ_secret_YoVTWqbfBRp3kW20QmtZmSNKJ'
        data = {
            'payment_confirmed': 'True',
            'client_secret': [test_client_secret],
        }
        self.client.post('/checkout/payment_confirmed/', data)
        self.assertEqual(len(mail.outbox), 1)


class TestCheckoutSucceededView(TestCase):

    def test_checkout_succeeded_view_template_and_status_code(self):
        order = Order.objects.create(
            order_number='test_order_number',
            full_name='a',
            email='a@a.com',
            phone_number=1234,
            town_or_city='a',
            street_address1='a',
            country='b',
            pid='test_pid',
        )
        url = f'/checkout/checkout_succeeded/{order.pid}'
        response = self.client.get(url)
        self.assertTemplateUsed('checkout/checkout_succeeded.html')
        self.assertEqual(response.status_code, 200)


class TestStaffOrderList(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.test_user = User.objects.create(
            username='user',
            password='pass',
            email='admin@test.com',
            is_staff=True)

    def test_staff_order_list_redirects_for_non_staff_user(self):
        url = '/checkout/staff_order_list/'
        response = self.client.get(url, follow=True)
        self.assertIn('accounts/login', str(response.redirect_chain[0]))

    def test_staff_order_list_template_and_status_code(self):
        self.client.force_login(self.test_user)
        url = '/checkout/staff_order_list/'
        response = self.client.get(url)
        self.assertTemplateUsed('checkout/staff_order_list.html')
        self.assertEqual(response.status_code, 200)


class TestStaffOrderDetail(TestCase):

    test_standard_price = 20

    @classmethod
    def setUpTestData(cls):
        cls.order = Order.objects.create(
            full_name='name',
            email='name@email.com',
            phone_number='1234',
            country="countr",
            town_or_city="town",
            street_address1="1",
        )
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
        cls.line_item = OrderLineItem.objects.create(
            order=cls.order,
            product=cls.test_product,
            quantity=1, 
        )

    def test_staff_order_list_redirects_for_non_staff_user(self):
        url = f'/checkout/staff_order_detail/{self.order.id}/'
        response = self.client.get(url, follow=True)
        self.assertIn('accounts/login', str(response.redirect_chain[0]))

    def test_staff_order_detail_template_and_status_code(self):
        self.client.force_login(self.test_user)
        url = f'/checkout/staff_order_detail/{self.order.id}/'
        response = self.client.get(url)
        self.assertTemplateUsed('checkout/staff_order_detail.html')
        self.assertEqual(response.status_code, 200)

    def test_staff_order_detail_post_method_updates_order_fullfilled_flag(self):
        self.client.force_login(self.test_user)
        url = '/checkout/staff_order_detail/'
        data = {
            'fulfilled': {self.order.pk},
        }
        response = self.client.post(url, data)
        id = self.order.pk
        order = Order.objects.get(pk=id)
        self.assertTrue(order.fulfilled)

    def test_staff_order_detail_post_method_redirects_to_order_list_page(self):
        self.client.force_login(self.test_user)
        url = '/checkout/staff_order_detail/'
        data = {
            'fulfilled': {self.order.pk},
        }
        response = self.client.post(url, data)
        self.assertRedirects(response=response, expected_url=reverse('staff_order_list'))
