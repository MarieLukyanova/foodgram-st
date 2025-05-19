from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.generics import ListAPIView
from django.shortcuts import get_object_or_404
from recipes.models import (Recipe, Ingredient, IngredientRecipe, Favorite, ShoppingCart, User)
from .serializers import (RecipeListSerializer, IngredientSerializer, FavoriteSerializer,
                             ShoppingCartSerializer, RecipeWriteSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from .permissions import IsOwnerOrAdminOrReadOnly
from .filters import IngredientSearchFilter, RecipeFilter
from .paginations import ApiPagination
from datetime import date



class IngredientViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        viewsets.GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class IngredientListView(ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        if name:
            return self.queryset.filter(name__icontains=name)
        return self.queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsOwnerOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, )
    pagination_class = ApiPagination
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeListSerializer
        return RecipeWriteSerializer

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if Favorite.objects.filter(author=user, recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже добавлен!'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not Favorite.objects.filter(author=user, recipe=recipe).exists():
            return Response({'errors': 'Объект не найден'}, status=status.HTTP_404_NOT_FOUND)
        Favorite.objects.get(author=user, recipe=recipe).delete()
        return Response({'message': 'Рецепт успешно удалён из избранного'}, status=status.HTTP_200_OK)


    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))
        user = self.request.user
        if request.method == 'POST':
            if ShoppingCart.objects.filter(author=user, recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже добавлен!'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingCartSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(author=user, recipe=recipe)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        if not ShoppingCart.objects.filter(author=user, recipe=recipe).exists():
            return Response({'errors': 'Объект не найден'}, status=status.HTTP_404_NOT_FOUND)
        ShoppingCart.objects.get(recipe=recipe).delete()
        return Response('Рецепт успешно удалён из списка покупок.', status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], permission_classes=[AllowAny], url_path='get-link')
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        url = request.build_absolute_uri(f'/api/recipes/{recipe.pk}/')
        return Response({'url': url}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        ingredients = (
            IngredientRecipe.objects
            .filter(recipe__shopping_cart__author=user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        today = date.today().strftime("%d-%m-%Y")
        shopping_list = f'{today}\nСписок покупок\n\n'

        for item in ingredients:
            shopping_list += (
                f'{item["ingredient__name"]}: {item["total_amount"]}{item["ingredient__measurement_unit"]}\n'
            )
        shopping_list += '\n\nFoodgram.2025'

        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shop_list.txt"'
        )
        return response
