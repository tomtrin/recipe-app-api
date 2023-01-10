from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


class RecipeModelTests(TestCase):

    def test_create_recipe(self):

        user = get_user_model().objects.create_user(
            email='test@example.com',
            name='Test Name',
            password='testpass123',
        )

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)
