from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Ingredient
from core.tests.helper import create_user

INGREDIENT_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


def create_ingredient(user, name='Ingredient1'):
    return Ingredient.objects.create(user=user, name=name)


class UnauthenticatedIngredientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_ingredient_list_fails(self):
        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_fails(self):
        res = self.client.post(INGREDIENT_URL, {'name': 'ingredient1'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_partial_update_fails(self):
        user = create_user()
        ingredient = create_ingredient(user, 'ingredient1')
        url = detail_url(ingredient.id)
        res = self.client.patch(url, {'name':'ingredient2'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_full_update_fails(self):
        user = create_user()
        ingredient = create_ingredient(user, 'ingredient1')
        url = detail_url(ingredient.id)
        res = self.client.put(url, {'name':'ingredient2'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_fails(self):
        user = create_user()
        ingredient = create_ingredient(user, 'ingredient1')
        url = detail_url(ingredient.id)
        res = self.client.delete(url, {'name':'ingredient2'})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedIngredientAPITests(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_ingredient_list(self):
        ingredient1 = create_ingredient(self.user, 'Ingredient1')
        ingredient2 = create_ingredient(self.user, 'Ingredient2')
        ingredient3 = create_ingredient(self.user, 'Ingredient3')

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(ingredient3.name, res.data[0].values())
        self.assertIn(ingredient2.name, res.data[1].values())
        self.assertIn(ingredient1.name, res.data[2].values())

    def test_ingredient_list_limited_to_user(self):
        ingredient1 = create_ingredient(self.user, 'Ingredient1')

        other_user = create_user(email='other@example.com')
        ingredient3 = create_ingredient(other_user, 'Ingredient2')

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(ingredient1.name, res.data[0]['name'])
        self.assertEqual(ingredient1.id, res.data[0]['id'])

    def test_create_ingredient(self):

        payload = {
            'name': 'Ingredient1'
        }

        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        ingredient = Ingredient.objects.get(id=res.data['id'])

        self.assertEqual(ingredient.user, self.user)
        self.assertEqual(ingredient.name, payload['name'])

    def test_partial_update_ingredient(self):
        ingredient = create_ingredient(self.user, 'Ingredient1')

        payload = {
            'name': 'Ingredient2'
        }

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])

    def test_partial_update_ingredient_from_other_user_fails(self):
        user = create_user(email='Other@example.com')
        ingredient = create_ingredient(user, 'Ingredient1')

        payload = {
            'name': 'Ingredient2'
        }

        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(ingredient.name, payload['name'])

    def test_full_update_ingredient(self):
        ingredient = create_ingredient(self.user, 'Ingredient1')

        payload = {
            'name': 'Ingredient2'
        }

        url = detail_url(ingredient.id)
        res = self.client.put(url, payload)
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(ingredient.name, payload['name'])

    def test_full_update_ingredient_from_other_user_fails(self):
        user = create_user(email='Other@example.com')
        ingredient = create_ingredient(user, 'Ingredient1')

        payload = {
            'name': 'Ingredient2'
        }

        url = detail_url(ingredient.id)
        res = self.client.put(url, payload)
        ingredient.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertNotEqual(ingredient.name, payload['name'])

    def test_delete(self):
        ingredient = create_ingredient(self.user, 'Ingredient1')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        ingredients = Ingredient.objects.filter(id=ingredient.id)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ingredients)

    def test_get_ingredient(self):
        ingredient = create_ingredient(self.user, 'Ingredient1')

        url = detail_url(ingredient.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for k,v in res.data.items():
            self.assertEqual(getattr(ingredient, k), v)

    def test_get_ingredient_for_other_user_fails(self):
        other_user = create_user(email='other@example.com')
        ingredient = create_ingredient(other_user, 'Ingredient1')

        url = detail_url(ingredient.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)