from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


class PasswordResetFlowTests(TestCase):
    @override_settings(EMAIL_BACKEND='django.notifications.mail.backends.locmem.EmailBackend')
    def test_password_reset_email_and_confirm_link(self):
        user = User.objects.create_user(username='alice', email='alice@example.com', password='oldpass123')

        response = self.client.post(reverse('accounts:password_reset'), {'email': user.email})
        self.assertRedirects(response, reverse('accounts:password_reset_done'))

        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body
        self.assertIn('password-reset-confirm', body)
        self.assertIn('http', body)
