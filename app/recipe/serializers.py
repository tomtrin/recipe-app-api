from rest_framework import serializers
from core.models import Recipe


def get_model():
    return Recipe


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_model()
        fields = ['id', 'title', 'time_minutes', 'rating', 'link']
        read_only_fields = ['id']


class RecipeDetailSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
