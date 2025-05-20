from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Q, F
from django.urls import reverse
from users.models import User


class Ingredient(models.Model):
    name = models.CharField(verbose_name='Название', max_length=200,
                            db_index=True, help_text='Введите название ингредиента')
    measurement_unit = models.CharField(verbose_name='Единица измерения', max_length=200,
                                        help_text='Введите единицы измерения')

    class Meta:
        ordering = ['id']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    author = models.ForeignKey(User, verbose_name='Автор', on_delete=models.CASCADE, help_text='Автор рецепта')
    ingredients = models.ManyToManyField(Ingredient, through='IngredientRecipe', verbose_name='Ингредиент')
    text = models.TextField(verbose_name='Описание', help_text='Описание рецепта')
    name = models.CharField(verbose_name='Название', max_length=200,
                            help_text='Введите название рецепта', db_index=True)
    cooking_time = models.PositiveSmallIntegerField(verbose_name='Время приготовления',
                                                validators=[MinValueValidator(1, 'Минимальное время приготовления')],
                                                    help_text='Время приготовления рецепта в минутах')
    image = models.ImageField(verbose_name='Картинка рецепта', upload_to='',
                              help_text='Добавьте изображение рецепта')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ['-id']
        default_related_name = 'recipe'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'author'], name='unique_recipe')]


class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='recipe_ingredients', verbose_name='Название',
                               on_delete=models.CASCADE, help_text='Выберите рецепт')
    ingredient = models.ForeignKey(Ingredient, verbose_name='Ингредиент',
                                   on_delete=models.CASCADE, help_text='Укажите ингредиенты')
    amount = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1, 'Минимальное количество ингредиентов 1')],
        verbose_name='Количество', help_text='Укажите количество ингредиента')

    class Meta:
        verbose_name = 'Cостав рецепта'
        verbose_name_plural = 'Состав рецепта'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredients')]

    def __str__(self):
        return f'{self.ingredient} {self.amount}'

    def get_absolute_url(self):
        return reverse('recipe-detail', kwargs={'pk': self.pk})


class ShoppingCart(models.Model):
    author = models.ForeignKey(User, related_name='shopping_cart',
                               on_delete=models.CASCADE, verbose_name='Пользователь')
    recipe = models.ForeignKey(Recipe, related_name='shopping_cart', verbose_name='Рецепт для приготовления',
                               on_delete=models.CASCADE, help_text='Выберите рецепт')

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [models.UniqueConstraint(fields=['author', 'recipe'], name='unique_cart')]

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    author = models.ForeignKey(User, related_name='favorite', on_delete=models.CASCADE, verbose_name='Автор')
    recipe = models.ForeignKey(Recipe, related_name='favorite', on_delete=models.CASCADE, verbose_name='Рецепты')

    class Meta:
        verbose_name = 'Избранные рецепты'
        verbose_name_plural = 'Избранные рецепты'
        constraints = [models.UniqueConstraint(fields=['author', 'recipe'], name='unique_favorite')]

    def __str__(self):
        return f'{self.recipe}'


class Follow(models.Model):
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='follower',
                             on_delete=models.CASCADE, help_text='Текущий пользователь')
    author = models.ForeignKey(User, verbose_name='Подписка', related_name='followed',
                               on_delete=models.CASCADE, help_text='Подписаться на автора')

    class Meta:
        verbose_name = 'Мои подписки'
        verbose_name_plural = 'Мои подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'], name='unique_following'),
            models.CheckConstraint(check=~Q(user=F('author')), name='no_self_following')]

    def __str__(self):
        return f'Пользователь {self.user} подписан на {self.author}'
