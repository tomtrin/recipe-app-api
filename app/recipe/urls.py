""""
URL mappings for the recipe API
"""
from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from recipe import views
from rest_framework_nested import routers


router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)
router.register('ingredients', views.IngredientViewSet)

recipe_ingredients_router = routers.NestedDefaultRouter(
    router,
    'recipes',
    lookup='recipe'
)

recipe_ingredients_router.register(
    'recipe_ingredients',
    views.RecipeIngredientViewSet,
    basename='recipe-ingredient'
)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
    path('', include(recipe_ingredients_router.urls))
]
