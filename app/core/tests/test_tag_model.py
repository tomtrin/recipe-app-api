from django.test import TestCase
from core.tests.helper import create_user
from core import models


class TagModelTests(TestCase):

    def test_create_tag(self):
        user = create_user()
        tag = models.Tag.objects.create(
            user=user,
            name='My Tag'
        )

        self.assertEqual(str(tag), tag.name)
