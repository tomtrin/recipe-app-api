from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status
from core.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
)

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    return reverse('recipe:recipe-detail', args=[recipe_id])


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


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UnauthenticatedRecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_recipe_list_fails(self):
        res = self.client.get(RECIPES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_recipe_details_fails(self):
        user = get_user_model().objects.create_user(
            email='test2@example.com',
            password='test2pass123'
        )
        recipe = create_recipe(user=user)
        res = self.client.get(detail_url(recipe_id=recipe.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRecipeAPITests(TestCase):

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            name='Test Name',
            password='testpass123',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_returns_required_fields(self):
        create_recipe(self.user)
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        keys = res.data[0].keys()
        self.assertIn('title', keys)
        self.assertIn('rating', keys)
        self.assertIn('time_minutes', keys)
        self.assertNotIn('description', keys)

    def test_list_recipes_ordered_by_id_desc(self):
        recipe_values = [
            {'title': 'Recipe 1', 'description': 'Text 1', 'time_minutes': 5},
            {'title': 'Recipe 2', 'description': 'Text 2', 'time_minutes': 10},
            {'title': 'Recipe 3', 'description': 'Text 3', 'time_minutes': 15},
        ]

        for recipe_value in recipe_values:
            create_recipe(self.user, **recipe_value)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn('Recipe 3', res.data[0].values())
        self.assertIn('Recipe 2', res.data[1].values())
        self.assertIn('Recipe 1', res.data[2].values())

    def test_list_items_limited_to_user(self):
        other_user = create_user(
            email='test2@example.com',
            password='test2pass123'
        )

        create_recipe(user=self.user)
        create_recipe(user=other_user, title='Another Recipe')

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertNotIn('Another Recipe', res.data)
        self.assertEqual(len(res.data), 1)

    def test_get_recipe_details(self):
        recipe = create_recipe(user=self.user)

        res = self.client.get(detail_url(recipe_id=recipe.id))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        keys = res.data.keys()
        self.assertIn('title', keys)
        self.assertIn('description', keys)
        self.assertIn('rating', keys)
        self.assertIn('time_minutes', keys)

    def test_create_recipe(self):
        payload = {
            'title': 'New Recipe',
            'description': 'Text 1',
            'time_minutes': 10,
            'rating': 5,
        }

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(id=res.data['id'])
        self.assertEqual(self.user, recipe.user)

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_create_recipe_missing_required_fields_fails(self):
        payload = {}

        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', res.data.keys())

    def test_partial_update(self):
        original_link = 'http://example.com/recipe_link'
        recipe = create_recipe(
            user=self.user,
            title='Sample title',
            link=original_link,
        )
        payload = {'title': 'New Title'}

        res = self.client.patch(detail_url(recipe_id=recipe.id), data=payload)
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        recipe = create_recipe(
            user=self.user,
            title='Sample title',
            description='Sample description',
            link='http://example.com/recipe_link',
            rating=5,
        )
        payload = {
            'title': 'New Title',
            'description': 'New Description',
            'link': 'http://example.com/new-recipe-link',
            'rating': 4,
        }

        res = self.client.put(detail_url(recipe_id=recipe.id), data=payload)
        recipe.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)

    def test_delete(self):
        recipe = create_recipe(user=self.user)

        res = self.client.delete(detail_url(recipe_id=recipe.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_get_other_user_recipe_fails(self):
        other_user = create_user(
            email='other@example.com',
            password='otherpass123',
        )
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_other_user_recipe_fails(self):
        other_user = create_user(
            email='other@example.com',
            password='otherpass123',
        )
        recipe = create_recipe(user=other_user)
        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, {'title': 'Another Title'})

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe_with_new_tags(self):
        payload = {
            'title': 'My Thai Recipe',
            'time_minutes': 30,
            'tags': [{'name': 'thai'}, {'name': 'dinner'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existin_tags(self):
        tag_indian = Tag.objects.create(user=self.user, name='indian')

        payload = {
            'title': 'My Indian Recipe',
            'time_minutes': 30,
            'tags': [{'name': 'indian'}, {'name': 'dinner'}]
        }

        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        tags = Tag.objects.filter(user=self.user)
        self.assertEqual(tags.count(), 2)

        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)

        recipe = recipes[0]
        self.assertIn(tag_indian, recipe.tags.all())
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)

    def test_update_recipe_with_new_tags(self):
        recipe = create_recipe(user=self.user)
        payload = {
            'tags': [{'name': 'thai'}]
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        new_tag = Tag.objects.get(user=self.user, name='thai')

        self.assertIn(new_tag, recipe.tags.all())

    def test_update_recipe_with_existing_tag(self):
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag1)

        tag2 = Tag.objects.create(user=self.user, name='tag2')
        payload = {
            'tags': [{'name': 'tag2'}]
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertIn(tag2, recipe.tags.all())
        self.assertNotIn(tag1, recipe.tags.all())

    def test_clear_recipe_tags(self):
        tag1 = Tag.objects.create(user=self.user, name='tag1')
        tag2 = Tag.objects.create(user=self.user, name='tag2')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag1)
        recipe.tags.add(tag2)

        payload = {
            'tags': []
        }

        url = detail_url(recipe_id=recipe.id)
        res = self.client.patch(url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.all().count(), 0)

    def test_get_recipe_with_ingredient(self):
        recipe = create_recipe(user=self.user)
        ingredient = Ingredient.objects.create(
            user=self.user, name='chickpeas')
        recipe.recipe_ingredients.add(RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            units=RecipeIngredient.CUP,
            quantity=2
        ))
        recipe.save()

        url = detail_url(recipe_id=recipe.id)
        res = self.client.get(url)
        recipe_ingredients_data = res.data['recipe_ingredients'][0]
        self.assertEqual(
            recipe_ingredients_data['ingredient']['name'],
            ingredient.name)
