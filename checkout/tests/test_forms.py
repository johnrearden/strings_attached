from django.test import TestCase
from checkout.forms import OrderForm


class TestOrderForm(TestCase):

    def test_full_name_is_required(self):
        test_form = OrderForm({
            'full_name': '',
            'email': 'name@email.com',
            'phone_number': 123123123,
            'country': 'country',
            'street_address1': 'address1',
            'town_or_city': 'town',
        })
        self.assertFalse(test_form.is_valid())

    def test_email_is_required(self):
        test_form = OrderForm({
            'full_name': 'name',
            'email': '',
            'phone_number': 123123123,
            'country': 'country',
            'street_address1': 'address1',
            'town_or_city': 'town',
        })
        self.assertFalse(test_form.is_valid())

    def test_phone_number_is_required(self):
        test_form = OrderForm({
            'full_name': 'name',
            'email': 'name@email.com',
            'phone_number': '',
            'country': 'country',
            'street_address1': 'address1',
            'town_or_city': 'town',
        })
        self.assertFalse(test_form.is_valid())

    def test_country_is_required(self):
        test_form = OrderForm({
            'full_name': 'country',
            'email': 'name@email.com',
            'phone_number': 123123123,
            'country': '',
            'street_address1': 'address1',
            'town_or_city': 'town',
        })
        self.assertFalse(test_form.is_valid())

    def test_street_address1_is_required(self):
        test_form = OrderForm({
            'full_name': 'name',
            'email': 'name@email.com',
            'phone_number': 123123123,
            'country': 'country',
            'street_address1': '',
            'town_or_city': 'town',
        })
        self.assertFalse(test_form.is_valid())

    def test_town_or_city_is_required(self):
        test_form = OrderForm({
            'full_name': 'name',
            'email': 'name@email.com',
            'phone_number': 123123123,
            'country': 'country',
            'street_address1': 'address1',
            'town_or_city': '',
        })
        self.assertFalse(test_form.is_valid())
