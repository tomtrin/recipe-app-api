from rest_framework import serializers
from core.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    ingredient = IngredientSerializer(many=False)

    def _get_or_create_ingredient(self, ingredient):
        auth_user = self.context['request'].user
        ingredient_obj, created = Ingredient.objects.get_or_create(
            user=auth_user,
            **ingredient
        )

        return ingredient_obj

    def update(self, instance, validated_data):
        ingredient = validated_data.pop('ingredient', None)
        if ingredient is not None:
            ingredient_obj = self._get_or_create_ingredient(ingredient)
            instance.ingredient = ingredient_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'recipe', 'ingredient', 'units', 'quantity']
        read_only_fields = ['id']

    def create(self, validated_data):
        ingredient = validated_data.pop('ingredient', [])
        ingredient.update({'name': ingredient['name'].lower()})

        ingredient_obj = self._get_or_create_ingredient(ingredient)
        recipe_ingredient = RecipeIngredient.objects.create(
            ingredient=ingredient_obj, **validated_data)

        return recipe_ingredient


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'rating', 'link', 'tags']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):
    recipe_ingredients = RecipeIngredientSerializer(
        many=True, required=False, read_only=False)

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + \
            ['description', 'recipe_ingredients']

    def _get_or_create_tags(self, tags, instance):
        auth_user = self.context['request'].user
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            instance.tags.add(tag_obj)

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])

        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(tags, recipe)

        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
