from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, IngredientViewSet
from users.views import UserViewSet


router = DefaultRouter()
router.register('users', UserViewSet)
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('ingredients', IngredientViewSet)

urlpatterns = [
    path('', include(router.urls)),
    re_path(r'auth/', include('djoser.urls.authtoken')),
]
