"""
Tests for the User API
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')


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
