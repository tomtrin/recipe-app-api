from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import (
    viewsets,
    mixins,
)

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeIngredientSerializer,
)
from core.models import (
    Recipe,
    Tag,
    Ingredient,
    RecipeIngredient,
)


class RecipeViewSet(viewsets.ModelViewSet):
    """ View for managing recipe APIs"""
    serializer_class = RecipeDetailSerializer
    queryset = Recipe.objects.prefetch_related('recipe_ingredients')
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        if self.action == 'list':
            return RecipeSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BaseRecipeAttrViewSet(
        mixins.ListModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        viewsets.GenericViewSet):

    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseRecipeAttrViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeIngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = RecipeIngredientSerializer
    queryset = RecipeIngredient.objects.all()

    def get_queryset(self):
        return self.queryset.filter(
            recipe__user=self.request.user).order_by('ingredient')

    def perform_create(self, serializer):
        serializer.save()
