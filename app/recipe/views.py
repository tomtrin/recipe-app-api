from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from rest_framework.decorators import action
from rest_framework.response import Response

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
    TagSerializer,
    IngredientSerializer,
    RecipeIngredientSerializer,
    RecipeImageSerializer,
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
        elif self.action == 'upload_image':
            return RecipeImageSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
