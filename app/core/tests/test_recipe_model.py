from django.test import TestCase
from core.tests.helper import create_user
from core import models


def create_tag(user, name):
    return models.Tag.objects.create(user=user, name=name)


class RecipeModelTests(TestCase):

    def test_create_recipe(self):

        user = create_user()

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_recipe_with_tags(self):

        user = create_user()
        tag1 = create_tag(user, 'tag1')
        tag2 = create_tag(user, 'tag2')

        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            description='Sample recipe description.',
        )

        recipe.tags.add(tag1)
        recipe.tags.add(tag2)
        recipe_tags = recipe.tags.all()

        self.assertIn(tag1, recipe_tags)
        self.assertIn(tag2, recipe_tags)
