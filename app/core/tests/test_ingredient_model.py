from django.test import TestCase
from core.models import Ingredient
from core.tests.helper import create_user


class IngredientModelTest(TestCase):

    def test_create(self):
        user = create_user()
        ingredient = Ingredient.objects.create(
            user=user,
            name='Chickpeas',
        )

        self.assertEqual(str(ingredient), 'Chickpeas')
