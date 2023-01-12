from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Tag
from core.tests.helper import create_user

TAG_URL = reverse('recipe:tag-list')


def detail_url(tag_id):
    return reverse('recipe:tag-detail', args=[tag_id])


def create_tag(user, name='Tag1'):
    return Tag.objects.create(user=user, name=name)


class UnauthenticatedTagAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_tag_list_fails(self):
        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_fails(self):
        res = self.client.post(TAG_URL, {'name': 'tag1'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_fails(self):
        user = create_user()
        tag = create_tag(user, 'tag1')
        url = detail_url(tag.id)
        res = self.client.patch(url, {'name':'tag2'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_full_update_fails(self):
        user = create_user()
        tag = create_tag(user, 'tag1')
        url = detail_url(tag.id)
        res = self.client.put(url, {'name':'tag2'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_fails(self):
        user = create_user()
        tag = create_tag(user, 'tag1')
        url = detail_url(tag.id)
        res = self.client.delete(url, {'name':'tag2'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTagAPITests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_tag_list(self):
        tag1 = create_tag(self.user, 'Tag1')
        tag2 = create_tag(self.user, 'Tag2')
        tag3 = create_tag(self.user, 'Tag3')

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(tag3.name, res.data[0].values())
        self.assertIn(tag2.name, res.data[1].values())
        self.assertIn(tag1.name, res.data[2].values())

    def test_tag_list_limited_to_user(self):
        tag1 = create_tag(self.user, 'Tag1')

        other_user = create_user(email='other@example.com')
        tag3 = create_tag(other_user, 'Tag2')

        res = self.client.get(TAG_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(tag1.name, res.data[0]['name'])
        self.assertEqual(tag1.id, res.data[0]['id'])

    def test_create_tag(self):

        payload = {
            'name': 'Tag1'
        }

        res = self.client.post(TAG_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        tag = Tag.objects.get(id=res.data['id'])

        self.assertEqual(tag.user, self.user)
        self.assertEqual(tag.name, payload['name'])

    def test_partial_update_tag(self):
        tag = create_tag(self.user, 'Tag1')

        payload = {
            'name': 'Tag2'
        }

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_partial_update_tag_from_other_user_fails(self):
        user = create_user(email='Other@example.com')
        tag = create_tag(user, 'Tag1')

        payload = {
            'name': 'Tag2'
        }

        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(tag.name, payload['name'])

    def test_full_update_tag(self):
        tag = create_tag(self.user, 'Tag1')

        payload = {
            'name': 'Tag2'
        }

        url = detail_url(tag.id)
        res = self.client.put(url, payload)
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.name, payload['name'])

    def test_full_update_tag_from_other_user_fails(self):
        user = create_user(email='Other@example.com')
        tag = create_tag(user, 'Tag1')

        payload = {
            'name': 'Tag2'
        }

        url = detail_url(tag.id)
        res = self.client.put(url, payload)
        tag.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(tag.name, payload['name'])

    def test_delete(self):
        tag = create_tag(self.user, 'Tag1')

        url = detail_url(tag.id)
        res = self.client.delete(url)
        tags = Tag.objects.filter(id=tag.id)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(tags)

    def test_get_tag(self):
        tag = create_tag(self.user, 'Tag1')

        url = detail_url(tag.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for k,v in res.data.items():
            self.assertEqual(getattr(tag, k), v)

    def test_get_tag_for_other_user_fails(self):
        other_user = create_user(email='other@example.com')
        tag = create_tag(other_user, 'Tag1')

        url = detail_url(tag.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)