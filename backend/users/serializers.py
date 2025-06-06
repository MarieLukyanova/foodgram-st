from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ValidationError
from djoser.serializers import TokenCreateSerializer
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Follow, Recipe
from .models import User
import api.serializers


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()
    class Meta:
        model = User
        fields = ('avatar',)


class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        email = attrs.get('email')

        if email and '@' not in email:
            raise ValidationError({'email': 'Пожалуйста, введите email, а не имя пользователя.'})

        return super().validate(attrs)



class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'password', 'avatar', 'is_subscribed')
        extra_kwargs = {'password': {'write_only': True}, 'is_subscribed': {'read_only': True}}

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(user=user, author=obj).exists()
        return False

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class FollowSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Follow
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(
                user=obj.user,
                author=obj.author).exists()
        return False

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = Recipe.objects.filter(author=obj.author)
        if limit and limit.isdigit():
            recipes = recipes[:int(limit)]
        return api.serializers.RecipeMiniSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()

    def validate(self, data):
        author = self.context.get('author')
        user = self.context.get('request').user
        if Follow.objects.filter(author=author, user=user).exists():
            raise ValidationError(
                detail='Вы уже подписаны на этого пользователя!',
                code=status.HTTP_400_BAD_REQUEST)
        if user == author:
            raise ValidationError(
                detail='Невозможно подписаться на себя!',
                code=status.HTTP_400_BAD_REQUEST)
        return data
