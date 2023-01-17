"""
Database Models.
"""

import uuid
import os

from django.conf import settings
from django.db import models
from django.core.validators import validate_email
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


def recipe_image_file_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'

    return os.path.join('uploads', 'recipe', filename)


class UserManager(BaseUserManager):
    """ Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """ Create, save and return a new user. """
        if not email:
            raise ValueError('User must have an email address.')

        validate_email(email)

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """ Create, save and return a super user. """
        return self.create_user(email, password,
                                is_staff=True,
                                is_superuser=True)


class User(AbstractBaseUser, PermissionsMixin):
    """ User in the system """

    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField(blank=True)
    rating = models.IntegerField(null=True, blank=True)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path)

    def __str__(self):
        return self.title


class Tag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )

    NONE = ''
    TEASPOON = 'tsp'
    TABLESPOON = 'tbsp'
    CUP = 'cup'
    OUNCE = 'oz'
    MILLITERS = 'ml'
    LITER = 'l'
    MILGRAM = 'mg'
    GRAM = 'gm'
    KILOGRAM = 'kg'

    UNITS_OF_MEASUREMENT = (
        (NONE, 'None'),
        (TEASPOON, 'Teaspoon'),
        (TABLESPOON, 'Tablespoon'),
        (CUP, 'Cup'),
        (OUNCE, 'Ounce'),
        (MILLITERS, 'Milliter'),
        (LITER, 'Litre'),
        (MILGRAM, 'Milgram'),
        (GRAM, 'Gram'),
        (KILOGRAM, 'Kilogram'),
    )

    quantity = models.IntegerField()
    units = models.CharField(
        max_length=10,
        choices=UNITS_OF_MEASUREMENT,
        default=NONE,
    )

    def __str__(self):
        if self.units == self.NONE:
            return f"{self.quantity} {self.ingredient}"

        return f"{self.quantity} {self.units} {self.ingredient}"
