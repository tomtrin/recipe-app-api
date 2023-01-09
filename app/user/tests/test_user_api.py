"""
Tests for the User API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UnauthenticatedUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpass123"
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_with_existing_email_fails(self):
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpass123"
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        existing_users = get_user_model().objects.filter(
            email=payload['email']
        )
        self.assertEqual(len(existing_users), 1)

    def test_create_user_with_password_less_than_5_chars_fails(self):
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "four"
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_user_with_missing_field_fails(self):
        payload = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "four"
        }
        required_fields = ['name', 'email', 'password']

        for required_field in required_fields:
            bad_payload = payload.copy()
            bad_payload.pop(required_field, None)

            res = self.client.post(CREATE_USER_URL, bad_payload)
            error_details = str(res.data[required_field][0])

            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(error_details, 'This field is required.')

    def test_create_token_for_user_successful(self):
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test123pass',
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_with_bad_email_fails(self):
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test123pass',
        }

        create_user(**user_details)

        payload = {
            'email': 'none_existing@example.com',
            'password': user_details['password'],
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_bad_password_fails(self):
        user_details = {
            'name': 'Test Name',
            'email': 'test@example.com',
            'password': 'test123pass',
        }

        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': 'incorrect_pw',
        }

        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_profile_without_auth_token_fails(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserApiTests(TestCase):

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            name='Test Name',
            password='testpass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_with_token_successful(self):
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,
                         {
                             'name': self.user.name,
                             'email': self.user.email,
                         }
                         )

    def test_post_me_not_allowed(self):
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        payload = {'name': 'Updated Name', 'password': 'newpassword123'}

        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
