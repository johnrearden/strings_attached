from django.test import TestCase


class TestWelcomeViews(TestCase):

    def test_welcome_view(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'welcome/welcome.html', 'base.html')
        self.assertEqual(response.status_code, 200)
