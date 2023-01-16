from django.test import TestCase
from core.models import (
    Recipe,
    Ingredient,
    RecipeIngredient,
)
from core.tests.helper import create_user


class RecipeIngredientModelTest(TestCase):

    def test_create(self):
        user = create_user()
        recipe = Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            description='Sample recipe description.',
        )
        ingredient = Ingredient.objects.create(
            user=user,
            name='Chickpeas',
        )
        recipeIngredient = RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            units=RecipeIngredient.CUP,
            quantity=2,
        )

        ingredient_amounts_from_db = RecipeIngredient.objects.filter(recipe=recipe)

        self.assertEqual(ingredient_amounts_from_db.count(), 1)
        self.assertEqual(ingredient_amounts_from_db[0].ingredient, ingredient)

    def test_tostring_with_unit(self):
        recipeIngredient = RecipeIngredient(
            ingredient=Ingredient(name='Chickpeas'),
            units=RecipeIngredient.CUP,
            quantity=2,
        )
        self.assertEqual(str(recipeIngredient), '2 cup Chickpeas')

    def test_tostring_with_no_unit(self):
        recipeIngredient = RecipeIngredient(
            ingredient=Ingredient(name='Apples'),
            units=RecipeIngredient.NONE,
            quantity=2,
        )
        self.assertEqual(str(recipeIngredient), '2 Apples')