from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):
    """ Test models."""

    def test_create_user_with_email_successful(self):

        email = 'test@example.com'
        password = 'testpass123'

        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalize(self):

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]

        for email, expected in sample_emails:

            user = get_user_model().objects.create_user(
                email=email,
                password='sample123'
            )

            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_value_error(self):

        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(
                email='',
                password='sample123'
            )

    def test_new_user_with_invalid_email_raises_validation_error(self):

        sample_emails = [
            'test1example.com',
            'test2@example',
            'test 3@example.com',
            'test4@example .com',
        ]

        for email in sample_emails:

            with self.assertRaises(ValidationError):
                get_user_model().objects.create_user(
                    email=email,
                    password='sample123'
                )

    def test_create_superuser(self):

        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'sample123',
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
