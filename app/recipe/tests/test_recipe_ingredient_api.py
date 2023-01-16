from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import Recipe, Ingredient, RecipeIngredient
from core.tests.helper import create_user


def recipe_ingredient_url(recipe_id):
    return reverse('recipe:recipe-ingredient-list', args=[recipe_id])


def detail_url(recipe_id, recipe_ingredient_id):
    return reverse('recipe:recipe-ingredient-detail', args=[recipe_id, recipe_ingredient_id])


def create_recipe_ingredient(recipe, ingredient, units=RecipeIngredient.CUP, quantity=1):
    return RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=ingredient,
        units=units,
        quantity=quantity,
    )


def create_recipe(user, **params):
    defaults = {
        'title': 'Recipe 1',
        'description': 'Text 1',
        'time_minutes': 5,
        'rating': 5,
    }
    defaults.update(params)

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


def create_ingredient(user, name='Ingredient1'):
    return Ingredient.objects.create(user=user, name=name)


class UnauthenticatedRecipeIngredientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_get_list_fails(self):
        recipe = create_recipe(create_user())
        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRecipeIngredientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(user=self.user)

    def test_get_recipe_ingredient(self):
        ingredient = create_ingredient(self.user)
        recipe = create_recipe(self.user)
        recipe_ingredient = create_recipe_ingredient(
            recipe=recipe, ingredient=ingredient)

        url = detail_url(recipe_id=recipe.id,
                         recipe_ingredient_id=recipe_ingredient.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['recipe'], recipe.id)
        self.assertEqual(res.data['ingredient']['name'], ingredient.name)

    def test_create_recipe_ingredient(self):
        recipe = create_recipe(self.user)

        ingredient_name = 'chickpeas'
        ingredient_units = RecipeIngredient.CUP
        ingredient_quantity = 1

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': ingredient_name},
            'units': ingredient_units,
            'quantity': ingredient_quantity
        }

        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe_ingredient_from_db = RecipeIngredient.objects.filter(
            recipe=recipe)
        self.assertTrue(recipe_ingredient_from_db.exists())
        self.assertEqual(
            recipe_ingredient_from_db.first().ingredient.name, ingredient_name)
        self.assertEqual(
            recipe_ingredient_from_db.first().units, ingredient_units)
        self.assertEqual(
            recipe_ingredient_from_db.first().quantity, ingredient_quantity)

    def test_create_recipe_ingredient_without_ingredient_fails(self):
        recipe = create_recipe(self.user)

        ingredient_units = RecipeIngredient.CUP
        ingredient_quantity = 1

        payload = {
            'recipe': recipe.id,
            'units': ingredient_units,
            'quantity': ingredient_quantity
        }

        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recipe_ingredient_without_quantity_fails(self):
        recipe = create_recipe(self.user)

        ingredient_units = RecipeIngredient.CUP

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': 'chickpeas'},
            'units': ingredient_units,
        }

        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recipe_ingredient_with_empty_unit_succeeds(self):
        recipe = create_recipe(self.user)

        ingredient_units = RecipeIngredient.NONE
        ingredient_quantity = 1

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': 'chickpeas'},
            'units': ingredient_units,
            'quantity': ingredient_quantity}

        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_recipe_ingredient_does_not_create_duplicate_ingredient(self):
        recipe = create_recipe(self.user)
        ingredient = create_ingredient(self.user, name='chickpeas')

        ingredient_units = RecipeIngredient.CUP
        ingredient_quantity = 1

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': ingredient.name},
            'units': ingredient_units,
            'quantity': ingredient_quantity
        }

        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        ingredients_from_db = Ingredient.objects.all()
        self.assertEqual(ingredients_from_db.count(), 1)


    def test_create_recipe_ingredient_ignores_ingredient_casing(self):
        recipe = create_recipe(self.user)
        ingredient = create_ingredient(self.user, name='chickpeas')

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': ingredient.name.upper()},
            'units': RecipeIngredient.CUP,
            'quantity': 2
        }

        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        ingredients_from_db = Ingredient.objects.all()
        self.assertEqual(ingredients_from_db.count(), 1)

    def test_create_recipe_ingredient_with_invalid_recipe_fails(self):
        recipe = create_recipe(self.user)

        invalid_recipe_id = 99999
        ingredient_name = 'chickpeas'
        ingredient_units = RecipeIngredient.CUP
        ingredient_quantity = 1

        payload = {
            'recipe': invalid_recipe_id,
            'ingredient': {'name': ingredient_name},
            'units': ingredient_units,
            'quantity': ingredient_quantity
        }

        url = recipe_ingredient_url(recipe_id=recipe.id)
        res = self.client.post(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_recipe_ingredient(self):
        recipe = create_recipe(self.user)
        ingredient = create_ingredient(self.user, 'Apples')
        recipe_ingredient = create_recipe_ingredient(
            recipe=recipe, ingredient=ingredient)

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': 'Pears'},
        }

        url = detail_url(recipe_id=recipe.id,
                         recipe_ingredient_id=recipe_ingredient.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe_ingredient.refresh_from_db()
        self.assertEqual(recipe_ingredient.ingredient.name, payload['ingredient']['name'])

        all_ingredients = Ingredient.objects.all()
        self.assertEqual(all_ingredients.count(), 2)

    def test_full_update_recipe_ingredient(self):
        recipe = create_recipe(self.user)
        ingredient = create_ingredient(self.user, 'Apples')
        recipe_ingredient = create_recipe_ingredient(
            recipe=recipe, ingredient=ingredient, units=RecipeIngredient.GRAM, quantity='10')

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': 'Apples'},
            'units': RecipeIngredient.CUP,
            'quantity': 1
        }

        url = detail_url(recipe_id=recipe.id,
                         recipe_ingredient_id=recipe_ingredient.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe_ingredient.refresh_from_db()
        self.assertEqual(recipe_ingredient.ingredient.name, payload['ingredient']['name'])
        self.assertEqual(recipe_ingredient.units, payload['units'])
        self.assertEqual(recipe_ingredient.quantity, payload['quantity'])

    def test_update_recipe_ingredient_for_other_user_fails(self):
        other_user = create_user(email='other@example.com')
        recipe = create_recipe(other_user)
        ingredient = create_ingredient(other_user, 'Apples')
        recipe_ingredient = create_recipe_ingredient(
            recipe=recipe, ingredient=ingredient)

        payload = {
            'recipe': recipe.id,
            'ingredient': {'name': 'Pears'},
        }

        url = detail_url(recipe_id=recipe.id,
                         recipe_ingredient_id=recipe_ingredient.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete(self):
        recipe = create_recipe(self.user)
        ingredient = create_ingredient(self.user)
        recipe_ingredient = create_recipe_ingredient(
            recipe=recipe, ingredient=ingredient)

        url = detail_url(recipe_id=recipe.id,
                         recipe_ingredient_id=recipe_ingredient.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        recipe_ingredients_from_db = RecipeIngredient.objects.all()
        self.assertEqual(recipe_ingredients_from_db.count(), 0)

    def test_delete_for_other_user_fails(self):
        other_user = create_user(email='other@example.com')
        recipe = create_recipe(other_user)
        ingredient = create_ingredient(other_user, 'Apples')
        recipe_ingredient = create_recipe_ingredient(
            recipe=recipe, ingredient=ingredient)

        url = detail_url(recipe_id=recipe.id,
                         recipe_ingredient_id=recipe_ingredient.id)

        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
